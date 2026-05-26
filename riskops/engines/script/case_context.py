"""Case context loader for the script recommendation demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = ROOT / "synthetic_data"
P4_FIELDS = {"id_no", "mobile_no", "customer_name", "bank_card_no", "address"}


def load_case_context(case_id: str) -> dict[str, Any]:
    """Load a P4-safe case context from synthetic parquet tables."""

    normalized_case_id = _normalize_case_id(case_id)
    dim_case = _read_parquet(DEFAULT_DATA_ROOT / "dim" / "dim_case.parquet")
    dim_customer = _read_parquet(DEFAULT_DATA_ROOT / "dim" / "dim_customer.parquet")
    case_status = _read_parquet(DEFAULT_DATA_ROOT / "dws" / "dws_case_status_snapshot_di.parquet")
    process = _read_parquet(DEFAULT_DATA_ROOT / "dws" / "dws_collection_process_wide_di.parquet")
    sms_log = _read_parquet(DEFAULT_DATA_ROOT / "ods" / "ods_sms_send_log.parquet")

    case_row = _single_row(dim_case, "case_id", normalized_case_id, "dim_case")
    customer_id = str(case_row.get("customer_id", ""))
    customer_row = _single_row(dim_customer, "customer_id", customer_id, "dim_customer")

    latest_status = _latest_row(case_status[case_status["case_id"].eq(normalized_case_id)], "stat_date")
    case_process = process[process["case_id"].eq(normalized_case_id)].copy()

    reference_time = _reference_time(case_status, process, sms_log)
    window_start = reference_time - pd.Timedelta(days=6)
    today_start = reference_time.normalize()

    case_process["stat_date"] = pd.to_datetime(case_process.get("stat_date"), errors="coerce")
    recent_process = case_process[case_process["stat_date"].between(window_start.normalize(), reference_time.normalize())]
    today_process = case_process[case_process["stat_date"].eq(today_start)]

    case_sms = sms_log[sms_log["case_id"].eq(normalized_case_id)].copy()
    case_sms["send_time"] = pd.to_datetime(case_sms.get("send_time"), errors="coerce")
    recent_sms = case_sms[case_sms["send_time"].between(window_start, reference_time + pd.Timedelta(days=1))]
    today_sms = case_sms[case_sms["send_time"].dt.normalize().eq(today_start)]

    ptp_process = case_process[pd.to_numeric(case_process.get("ptp_count"), errors="coerce").fillna(0).gt(0)]
    last_ptp = _latest_row(ptp_process, "stat_date")

    recent_action_count = _sum_int(recent_process, "action_count")
    recent_connected_count = _sum_int(recent_process, "connected_count")
    context = {
        "case_id": normalized_case_id,
        "customer_id_hash": str(customer_row.get("customer_id_hash", "")),
        "initial_dpd_bucket": str(case_row.get("initial_dpd_bucket", "")),
        "outstanding_amount": _float_or_zero(
            latest_status.get("outstanding_amount", case_row.get("initial_outstanding_amount", 0.0))
        ),
        "risk_level": str(_first_present(latest_status, "risk_level", customer_row.get("risk_level_current", ""))),
        "protect_flag": bool(case_row.get("protect_flag", False)),
        "complaint_flag": bool(case_row.get("complaint_flag", False)),
        "sensitive_flag": bool(case_row.get("sensitive_flag", customer_row.get("sensitive_flag", False))),
        "recent_action_count_7d": recent_action_count,
        "recent_sms_count_7d": int(len(recent_sms)),
        "recent_connect_rate": _safe_rate(recent_connected_count, recent_action_count),
        "last_ptp_date": _date_string(last_ptp.get("stat_date")),
        "last_ptp_amount": None,
        "ptp_fulfilled": _ptp_fulfilled(last_ptp),
        "current_vendor_id": str(_first_present(latest_status, "vendor_id", case_row.get("current_vendor_id", ""))),
        "current_line_id": str(_first_present(latest_status, "line_id", case_row.get("current_line_id", ""))),
        "_frequency_counts": {
            "sms": {"today": int(len(today_sms)), "week": int(len(recent_sms))},
            "ai_call": {
                "today": _sum_int(today_process, "ai_action_count"),
                "week": _sum_int(recent_process, "ai_action_count"),
            },
            "manual": {
                "today": max(_sum_int(today_process, "action_count") - _sum_int(today_process, "ai_action_count"), 0),
                "week": max(_sum_int(recent_process, "action_count") - _sum_int(recent_process, "ai_action_count"), 0),
            },
        },
    }
    return _drop_p4_fields(context)


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing script context input: {path}")
    return pd.read_parquet(path)


def _normalize_case_id(case_id: str) -> str:
    raw = str(case_id).strip()
    if raw.startswith("CASE-"):
        suffix = raw.removeprefix("CASE-")
        if suffix.isdigit():
            return f"CASE{int(suffix):08d}"
    return raw


def _single_row(frame: pd.DataFrame, key: str, value: str, table_name: str) -> pd.Series:
    rows = frame[frame[key].astype(str).eq(value)]
    if rows.empty:
        raise ValueError(f"{table_name} missing {key}={value}")
    return rows.iloc[0]


def _latest_row(frame: pd.DataFrame, date_column: str) -> pd.Series:
    if frame.empty or date_column not in frame.columns:
        return pd.Series(dtype=object)
    rows = frame.copy()
    rows[date_column] = pd.to_datetime(rows[date_column], errors="coerce")
    rows = rows.dropna(subset=[date_column])
    if rows.empty:
        return pd.Series(dtype=object)
    return rows.sort_values(date_column).iloc[-1]


def _reference_time(*frames: pd.DataFrame) -> pd.Timestamp:
    candidates = []
    for frame in frames:
        for column in ["stat_date", "send_time"]:
            if column in frame.columns and not frame.empty:
                value = pd.to_datetime(frame[column], errors="coerce").max()
                if pd.notna(value):
                    candidates.append(value)
    return max(candidates) if candidates else pd.Timestamp.now().normalize()


def _sum_int(frame: pd.DataFrame, column: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum())


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 6)


def _float_or_zero(value: Any) -> float:
    if pd.isna(value):
        return 0.0
    return float(value)


def _date_string(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.to_datetime(value).date().isoformat()


def _ptp_fulfilled(row: pd.Series) -> bool | None:
    if row.empty:
        return None
    ptp_count = int(pd.to_numeric(pd.Series([row.get("ptp_count", 0)]), errors="coerce").fillna(0).iloc[0])
    if ptp_count <= 0:
        return None
    fulfilled_count = int(pd.to_numeric(pd.Series([row.get("ptp_fulfilled_count", 0)]), errors="coerce").fillna(0).iloc[0])
    return fulfilled_count > 0


def _first_present(row: pd.Series, key: str, fallback: Any) -> Any:
    if not row.empty and key in row and pd.notna(row.get(key)):
        return row.get(key)
    return fallback


def _drop_p4_fields(context: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in context.items() if key not in P4_FIELDS}
