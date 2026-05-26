"""Local data query tools for the RiskOps TUI."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "synthetic_data"
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
SYNTHETIC_NOTE = "基于合成数据，不代表真实业务"
SEGMENT_COLUMNS = {"channel_code", "province", "risk_level", "product_code", "score_band"}
P4_COLUMNS = {"customer_name", "id_no", "mobile_no", "bank_card_no", "address"}


def query_recovery_rate(
    segment_col: str | None = None,
    segment_val: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
) -> dict[str, Any]:
    """Query D7 recovery rate time series."""

    params = {
        "segment_col": segment_col,
        "segment_val": segment_val,
        "date_start": date_start,
        "date_end": date_end,
    }
    if segment_col:
        fact = _build_recovery_fact()
        if segment_col not in SEGMENT_COLUMNS:
            return _tool_response("query_recovery_rate", params, [], 0, f"{SYNTHETIC_NOTE}；不支持的分组维度。")
        fact = _filter_dates(fact, date_start, date_end)
        fact = fact[fact[segment_col].astype(str).eq(str(segment_val))] if segment_val is not None else fact
        grouped = _aggregate_recovery(fact, ["stat_date", segment_col])
        return _tool_response("query_recovery_rate", params, _records(grouped, 366), len(grouped), SYNTHETIC_NOTE)

    dashboard = _filter_dates(_read_parquet("ads/ads_postloan_dashboard_di.parquet"), date_start, date_end)
    result = dashboard.sort_values("stat_date")[["stat_date", "recovery_rate_d7"]]
    return _tool_response("query_recovery_rate", params, _records(result, 366), len(result), SYNTHETIC_NOTE)


def query_anomalies(
    severity: str | None = None,
    metric_code: str | None = None,
) -> dict[str, Any]:
    """Query anomaly results."""

    payload = _read_json("anomalies/anomaly_results.json")
    anomalies = payload.get("anomalies", []) if isinstance(payload, dict) else []
    result = [
        item
        for item in anomalies
        if (severity is None or item.get("severity") == severity)
        and (metric_code is None or item.get("metric_code") == metric_code)
    ]
    return _tool_response("query_anomalies", {"severity": severity, "metric_code": metric_code}, result, len(result), SYNTHETIC_NOTE)


def query_top_drivers(top_n: int = 5) -> dict[str, Any]:
    """Query top attribution drivers."""

    payload = _read_json("attribution/attribution_results.json")
    attributions = payload.get("attributions", []) if isinstance(payload, dict) else []
    result = sorted(
        attributions,
        key=lambda item: (
            item.get("contribution_rank", 10**9),
            -abs(float(item.get("contribution_score", 0) or 0)),
        ),
    )[: max(int(top_n), 0)]
    return _tool_response("query_top_drivers", {"top_n": top_n}, result, len(result), SYNTHETIC_NOTE)


def query_roi_scenarios(scenario_id: str | None = None) -> dict[str, Any]:
    """Query ROI scenario results."""

    payload = _read_json("model_lab/roi_results.json")
    scenarios = payload.get("results", []) if isinstance(payload, dict) else []
    result = [item for item in scenarios if scenario_id is None or item.get("scenario_id") == scenario_id]
    return _tool_response("query_roi_scenarios", {"scenario_id": scenario_id}, result, len(result), SYNTHETIC_NOTE)


def query_vendor_performance(
    vendor_id: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
) -> dict[str, Any]:
    """Query vendor performance metrics."""

    data = _filter_dates(_read_parquet("ads/ads_vendor_performance_di.parquet"), date_start, date_end)
    if vendor_id:
        data = data[data["vendor_id"].astype(str).eq(str(vendor_id))]
    grouped = (
        data.groupby("vendor_id", as_index=False)
        .agg(
            action_count=("action_count", "sum"),
            connect_rate=("connect_rate", "mean"),
            ptp_rate=("ptp_rate", "mean"),
            ptp_keep_rate=("ptp_keep_rate", "mean"),
            call_coverage_rate=("call_coverage_rate", "mean"),
            complaint_rate=("complaint_rate", "mean"),
        )
        .sort_values("vendor_id")
    )
    if not grouped.empty:
        grouped["recovery_contribution"] = (
            grouped["action_count"] * grouped["ptp_rate"] * grouped["ptp_keep_rate"]
        ).round(6)
    return _tool_response(
        "query_vendor_performance",
        {"vendor_id": vendor_id, "date_start": date_start, "date_end": date_end},
        _records(grouped, 100),
        len(grouped),
        SYNTHETIC_NOTE,
    )


def query_collector_performance(
    vendor_id: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
) -> dict[str, Any]:
    """Query collector workload and performance metrics."""

    data = _filter_dates(_read_parquet("ads/ads_collector_performance_di.parquet"), date_start, date_end)
    if vendor_id:
        data = data[data["vendor_id"].astype(str).eq(str(vendor_id))]
    grouped = (
        data.groupby(["vendor_id", "collector_id"], as_index=False)
        .agg(
            daily_case_count=("action_count", "mean"),
            action_count=("action_count", "sum"),
            connect_rate=("connect_rate", "mean"),
            ptp_rate=("ptp_keep_rate", "mean"),
            ptp_keep_rate=("ptp_keep_rate", "mean"),
            complaint_count=("complaint_count", "sum"),
        )
        .sort_values(["vendor_id", "collector_id"])
    )
    if not grouped.empty:
        grouped["compliance_score"] = (1 - grouped["complaint_count"] / grouped["action_count"].replace(0, np.nan)).fillna(1).clip(0, 1)
    return _tool_response(
        "query_collector_performance",
        {"vendor_id": vendor_id, "date_start": date_start, "date_end": date_end},
        _records(grouped, 200),
        len(grouped),
        SYNTHETIC_NOTE,
    )


def query_segment_breakdown(
    segment_col: str,
    metric: str = "recovery_rate_d7",
    days: int = 30,
) -> dict[str, Any]:
    """Query recent segment metric averages and trend direction."""

    params = {"segment_col": segment_col, "metric": metric, "days": days}
    if segment_col not in SEGMENT_COLUMNS:
        return _tool_response("query_segment_breakdown", params, [], 0, f"{SYNTHETIC_NOTE}；不支持的分组维度。")
    if metric != "recovery_rate_d7":
        dashboard = _read_parquet("ads/ads_postloan_dashboard_di.parquet")
        if metric not in dashboard.columns:
            return _tool_response("query_segment_breakdown", params, [], 0, f"{SYNTHETIC_NOTE}；指标字段不存在。")
        return _tool_response("query_segment_breakdown", params, [], 0, f"{SYNTHETIC_NOTE}；该指标没有分段明细。")

    fact = _recent_days(_build_recovery_fact(), days)
    daily = _aggregate_recovery(fact, ["stat_date", segment_col])
    rows: list[dict[str, Any]] = []
    for value, group in daily.groupby(segment_col):
        ordered = group.sort_values("stat_date")
        values = ordered[metric].dropna()
        rows.append(
            {
                "segment_col": segment_col,
                "segment_val": _jsonable(value),
                "metric": metric,
                "avg_value": _round(values.mean()) if not values.empty else 0.0,
                "trend": _trend(values.iloc[0], values.iloc[-1]) if len(values) >= 2 else "flat",
                "first_value": _round(values.iloc[0]) if not values.empty else 0.0,
                "last_value": _round(values.iloc[-1]) if not values.empty else 0.0,
                "day_count": int(ordered["stat_date"].nunique()),
            }
        )
    rows = sorted(rows, key=lambda item: str(item["segment_val"]))
    return _tool_response("query_segment_breakdown", params, rows, len(rows), SYNTHETIC_NOTE)


def query_case_detail(
    case_id: str | None = None,
    customer_id: str | None = None,
) -> dict[str, Any]:
    """Query case base fields and recent status snapshots without P4 fields."""

    params = {"case_id": case_id, "customer_id": customer_id}
    if not case_id and not customer_id:
        return _tool_response("query_case_detail", params, [], 0, f"{SYNTHETIC_NOTE}；必须提供 case_id 或 customer_id。")

    cases = _read_parquet("dim/dim_case.parquet")
    snapshots = _read_parquet("dws/dws_case_status_snapshot_di.parquet")
    if case_id:
        cases = cases[cases["case_id"].astype(str).eq(str(case_id))]
        snapshots = snapshots[snapshots["case_id"].astype(str).eq(str(case_id))]
    if customer_id:
        cases = cases[cases["customer_id"].astype(str).eq(str(customer_id))]
        snapshots = snapshots[snapshots["customer_id"].astype(str).eq(str(customer_id))]

    snapshots = _recent_days(snapshots, 30)
    case_records = _drop_p4(cases)
    snapshot_records = _drop_p4(snapshots.sort_values(["case_id", "stat_date"]))
    grouped_snapshots: dict[str, list[dict[str, Any]]] = {}
    for item in _records(snapshot_records, 300):
        grouped_snapshots.setdefault(str(item.get("case_id")), []).append(item)

    result = []
    for item in _records(case_records.sort_values("case_id"), 100):
        item["recent_30d_snapshots"] = grouped_snapshots.get(str(item.get("case_id")), [])
        result.append(item)
    return _tool_response("query_case_detail", params, result, len(result), SYNTHETIC_NOTE)


def query_collection_process(
    segment_col: str | None = None,
    segment_val: str | None = None,
    days: int = 30,
) -> dict[str, Any]:
    """Query recent collection process metrics."""

    params = {"segment_col": segment_col, "segment_val": segment_val, "days": days}
    process = _recent_days(_build_process_fact(), days)
    if segment_col:
        if segment_col not in process.columns:
            return _tool_response("query_collection_process", params, [], 0, f"{SYNTHETIC_NOTE}；不支持的分组维度。")
        process = process[process[segment_col].astype(str).eq(str(segment_val))] if segment_val is not None else process

    if process.empty:
        return _tool_response("query_collection_process", params, [], 0, SYNTHETIC_NOTE)
    max_date = pd.to_datetime(process["stat_date"]).max()
    last_action = process.groupby("case_id", as_index=False)["stat_date"].max()
    last_action["days_since_last_action"] = (max_date - pd.to_datetime(last_action["stat_date"])).dt.days
    summary = {
        "segment_col": segment_col,
        "segment_val": segment_val,
        "action_count": int(process["action_count"].sum()),
        "connected_count": int(process["connected_count"].sum()),
        "connect_rate": _safe_rate(process["connected_count"].sum(), process["action_count"].sum()),
        "ptp_count": int(process["ptp_count"].sum()),
        "ptp_rate": _safe_rate(process["ptp_count"].sum(), process["connected_count"].sum()),
        "ai_coverage_rate": _safe_rate(process["ai_action_count"].sum(), process["action_count"].sum()),
        "days_since_last_action": _round(last_action["days_since_last_action"].mean()),
        "case_count": int(process["case_id"].nunique()),
    }
    return _tool_response("query_collection_process", params, [summary], 1, SYNTHETIC_NOTE)


def get_data_overview() -> dict[str, Any]:
    """List parquet files, row counts, columns, and date ranges."""

    rows = []
    for path in sorted(DATA_ROOT.rglob("*.parquet")):
        data = pd.read_parquet(path)
        date_col = _date_column(data)
        date_start = None
        date_end = None
        if date_col and not data.empty:
            dates = pd.to_datetime(data[date_col], errors="coerce")
            date_start = str(dates.min().date()) if dates.notna().any() else None
            date_end = str(dates.max().date()) if dates.notna().any() else None
        rows.append(
            {
                "file": str(path.relative_to(PROJECT_ROOT)),
                "row_count": int(len(data)),
                "columns": list(data.columns),
                "date_column": date_col,
                "date_start": date_start,
                "date_end": date_end,
            }
        )
    return _tool_response("get_data_overview", {}, rows, len(rows), SYNTHETIC_NOTE)


TOOLS = {
    "query_recovery_rate": query_recovery_rate,
    "query_anomalies": query_anomalies,
    "query_top_drivers": query_top_drivers,
    "query_roi_scenarios": query_roi_scenarios,
    "query_vendor_performance": query_vendor_performance,
    "query_collector_performance": query_collector_performance,
    "query_segment_breakdown": query_segment_breakdown,
    "query_case_detail": query_case_detail,
    "query_collection_process": query_collection_process,
    "get_data_overview": get_data_overview,
}


def call_tool(name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Call a registered local tool by name."""

    if name not in TOOLS:
        return _tool_response(name, params, [], 0, f"未知工具：{name}")
    return TOOLS[name](**params)


def _build_recovery_fact() -> pd.DataFrame:
    fact = _read_parquet("dws/dws_loan_status_snapshot_di.parquet").copy()
    fact["stat_date"] = pd.to_datetime(fact["stat_date"], errors="coerce")
    fact = fact[fact["dpd_bucket"].astype(str).eq("M1")].copy()

    loan = _read_parquet("dim/dim_loan.parquet")
    if "channel_code" not in fact.columns:
        fact = fact.merge(loan[["loan_id", "channel_code"]].drop_duplicates("loan_id"), on="loan_id", how="left")
    customer = _read_parquet("dim/dim_customer.parquet")
    fact = fact.merge(customer[["customer_id", "province", "risk_level_current"]].drop_duplicates("customer_id"), on="customer_id", how="left")
    if "risk_level" not in fact.columns:
        fact["risk_level"] = fact["risk_level_current"]
    else:
        fact["risk_level"] = fact["risk_level"].fillna(fact["risk_level_current"])

    score = _read_parquet("ods/ods_postloan_c_score.parquet")
    latest_score = score.sort_values("score_date").drop_duplicates("customer_id", keep="last")
    fact = fact.merge(latest_score[["customer_id", "score_level"]], on="customer_id", how="left")
    fact["score_band"] = fact["score_level"].fillna("UNKNOWN")
    for col in SEGMENT_COLUMNS:
        if col not in fact.columns:
            fact[col] = "UNKNOWN"
        fact[col] = fact[col].fillna("UNKNOWN").astype(str)
    return fact


def _build_process_fact() -> pd.DataFrame:
    process = _read_parquet("dws/dws_collection_process_wide_di.parquet").copy()
    process["stat_date"] = pd.to_datetime(process["stat_date"], errors="coerce")
    if "ai_action_count" not in process.columns:
        process["ai_action_count"] = process["ai_coverage_rate"] * process["action_count"]

    case = _read_parquet("dim/dim_case.parquet")
    process = process.merge(case[["case_id", "customer_id"]].drop_duplicates("case_id"), on="case_id", how="left")
    mapping = _read_parquet("dim/dim_case_loan_mapping.parquet")
    process = process.merge(mapping[["case_id", "loan_id"]].drop_duplicates("case_id"), on="case_id", how="left")
    loan = _read_parquet("dim/dim_loan.parquet")
    process = process.merge(
        loan[["loan_id", "channel_code", "product_code"]].drop_duplicates("loan_id"),
        on="loan_id",
        how="left",
    )
    customer = _read_parquet("dim/dim_customer.parquet")
    process = process.merge(
        customer[["customer_id", "province", "risk_level_current"]].drop_duplicates("customer_id"),
        on="customer_id",
        how="left",
    )
    process["risk_level"] = process["risk_level_current"]
    for col in ["channel_code", "product_code", "province", "risk_level", "vendor_id", "line_id", "collector_id"]:
        if col in process.columns:
            process[col] = process[col].fillna("UNKNOWN").astype(str)
    return process


def _aggregate_recovery(data: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if data.empty:
        columns = [*group_cols, "recovery_rate_d7", "due_amount", "repaid_amount_d7", "loan_count"]
        return pd.DataFrame(columns=columns)
    grouped = (
        data.groupby(group_cols, as_index=False)
        .agg(
            due_amount=("due_amount", "sum"),
            repaid_amount_d7=("repaid_amount_d7", "sum"),
            loan_count=("loan_id", "nunique"),
        )
        .sort_values(group_cols)
    )
    grouped["recovery_rate_d7"] = grouped.apply(lambda row: _safe_rate(row["repaid_amount_d7"], row["due_amount"]), axis=1)
    return grouped[[*group_cols, "recovery_rate_d7", "due_amount", "repaid_amount_d7", "loan_count"]]


def _read_parquet(relative_path: str) -> pd.DataFrame:
    return pd.read_parquet(DATA_ROOT / relative_path)


def _read_json(relative_path: str) -> Any:
    return json.loads((OUTPUT_ROOT / relative_path).read_text(encoding="utf-8"))


def _filter_dates(
    data: pd.DataFrame,
    date_start: str | None = None,
    date_end: str | None = None,
) -> pd.DataFrame:
    if "stat_date" not in data.columns:
        return data.copy()
    dates = pd.to_datetime(data["stat_date"], errors="coerce")
    mask = pd.Series(True, index=data.index)
    if date_start:
        mask &= dates >= pd.to_datetime(date_start)
    if date_end:
        mask &= dates <= pd.to_datetime(date_end)
    return data.loc[mask].copy()


def _recent_days(data: pd.DataFrame, days: int) -> pd.DataFrame:
    if data.empty or "stat_date" not in data.columns:
        return data.copy()
    dates = pd.to_datetime(data["stat_date"], errors="coerce")
    end = dates.max()
    start = end - pd.Timedelta(days=max(int(days), 1) - 1)
    return data.loc[dates.between(start, end)].copy()


def _records(data: pd.DataFrame, limit: int) -> list[dict[str, Any]]:
    if data.empty:
        return []
    return [
        {key: _jsonable(value) for key, value in row.items()}
        for row in data.head(limit).to_dict(orient="records")
    ]


def _tool_response(
    tool: str,
    params: dict[str, Any],
    result: list[dict[str, Any]],
    row_count: int,
    note: str,
) -> dict[str, Any]:
    clean_params = {key: _jsonable(value) for key, value in params.items() if value is not None}
    return {
        "tool": tool,
        "params": clean_params,
        "result": result,
        "row_count": int(row_count),
        "note": note,
    }


def _drop_p4(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop(columns=[col for col in data.columns if col in P4_COLUMNS], errors="ignore")


def _date_column(data: pd.DataFrame) -> str | None:
    for col in ["stat_date", "case_create_time", "due_date", "repay_date", "action_date", "score_date"]:
        if col in data.columns:
            return col
    return None


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, pd.Timestamp):
        return str(value.date())
    if isinstance(value, datetime):
        return str(value.date())
    if isinstance(value, date):
        return str(value)
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float):
        return _round(value)
    return value


def _round(value: Any) -> float:
    return round(float(value), 6)


def _safe_rate(numerator: Any, denominator: Any) -> float:
    denominator_value = float(denominator or 0)
    if denominator_value <= 0:
        return 0.0
    return _round(float(numerator or 0) / denominator_value)


def _trend(first: Any, last: Any) -> str:
    first_value = float(first)
    last_value = float(last)
    if last_value > first_value:
        return "up"
    if last_value < first_value:
        return "down"
    return "flat"
