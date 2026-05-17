"""Data decomposition helpers for M3-B attribution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from riskops.engines.anomaly.rules import window_bounds
from riskops.metrics.calculators.base import read_table


@dataclass(frozen=True)
class WindowSpec:
    baseline_start: pd.Timestamp
    baseline_end: pd.Timestamp
    recent_start: pd.Timestamp
    recent_end: pd.Timestamp

    @property
    def baseline_label(self) -> str:
        return f"{self.baseline_start.date()}~{self.baseline_end.date()}"

    @property
    def recent_label(self) -> str:
        return f"{self.recent_start.date()}~{self.recent_end.date()}"


def safe_rate(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator / denominator)


def load_optional_table(root: Path, layer: str, table: str, notes: list[str]) -> pd.DataFrame:
    try:
        return read_table(root, layer, table)
    except FileNotFoundError:
        notes.append(f"缺少 {layer}/{table}，相关维度或证据已降级。")
        return pd.DataFrame()


def infer_window(frame: pd.DataFrame, recent_days: int, baseline_days: int) -> WindowSpec:
    baseline_start, baseline_end, recent_start, recent_end = window_bounds(frame, "stat_date", recent_days, baseline_days)
    return WindowSpec(baseline_start, baseline_end, recent_start, recent_end)


def build_recovery_fact(root: Path, notes: list[str]) -> pd.DataFrame:
    loan = read_table(root, "dws", "dws_loan_status_snapshot_di").copy()
    required = {"stat_date", "loan_id", "customer_id", "product_code", "dpd_bucket", "due_amount", "repaid_amount_d7"}
    missing = required - set(loan.columns)
    if missing:
        raise KeyError(f"dws_loan_status_snapshot_di missing columns: {sorted(missing)}")

    loan["stat_date"] = pd.to_datetime(loan["stat_date"], errors="coerce")
    loan = loan[loan["dpd_bucket"].eq("M1")].copy()
    if loan.empty:
        notes.append("dws_loan_status_snapshot_di 中没有 M1 记录，归因退化为空结果。")
        return loan

    mapping = load_optional_table(root, "dim", "dim_case_loan_mapping", notes)
    if not mapping.empty and {"loan_id", "case_id"}.issubset(mapping.columns):
        loan = loan.merge(mapping[["loan_id", "case_id"]].drop_duplicates("loan_id"), on="loan_id", how="left")
    else:
        loan["case_id"] = pd.NA
        notes.append("缺少 loan_id 到 case_id 映射，vendor/line/collector/process 证据已降级。")

    case = load_optional_table(root, "dim", "dim_case", notes)
    case_cols = [
        col
        for col in [
            "case_id",
            "current_vendor_id",
            "current_line_id",
            "collector_id",
            "balance_segment",
            "initial_outstanding_amount",
        ]
        if col in case.columns
    ]
    if case_cols and "case_id" in case_cols:
        loan = loan.merge(case[case_cols].drop_duplicates("case_id"), on="case_id", how="left")
        loan["vendor_id"] = loan.get("current_vendor_id")
        loan["line_id"] = loan.get("current_line_id")
    else:
        loan["vendor_id"] = pd.NA
        loan["line_id"] = pd.NA
        loan["collector_id"] = pd.NA
        notes.append("dim_case 缺少关键分案字段，资源维度已降级。")

    case_status = load_optional_table(root, "dws", "dws_case_status_snapshot_di", notes)
    status_cols = [col for col in ["stat_date", "case_id", "vendor_id", "line_id", "collector_id"] if col in case_status.columns]
    if {"stat_date", "case_id"}.issubset(status_cols):
        daily_status = case_status[status_cols].copy()
        daily_status["stat_date"] = pd.to_datetime(daily_status["stat_date"], errors="coerce")
        daily_status = daily_status.drop_duplicates(["stat_date", "case_id"])
        loan = loan.merge(daily_status, on=["stat_date", "case_id"], how="left", suffixes=("", "_daily"))
        for col in ["vendor_id", "line_id", "collector_id"]:
            daily_col = f"{col}_daily"
            if daily_col in loan.columns:
                if col not in loan.columns:
                    loan[col] = loan[daily_col]
                else:
                    loan[col] = loan[col].fillna(loan[daily_col])
                loan = loan.drop(columns=[daily_col])
    else:
        notes.append("dws_case_status_snapshot_di 缺少分案字段，collector_id 维度可能降级。")

    dim_loan = load_optional_table(root, "dim", "dim_loan", notes)
    if not dim_loan.empty and {"loan_id", "channel_code"}.issubset(dim_loan.columns):
        loan = loan.merge(dim_loan[["loan_id", "channel_code"]].drop_duplicates("loan_id"), on="loan_id", how="left")
    else:
        loan["channel_code"] = pd.NA
        notes.append("dim_loan 缺少 channel_code，channel_code 维度已降级。")

    customer_daily = load_optional_table(root, "dws", "dws_customer_status_snapshot_di", notes)
    if not customer_daily.empty and {"stat_date", "customer_id", "risk_level", "total_outstanding_amount"}.issubset(customer_daily.columns):
        customer_daily = customer_daily[["stat_date", "customer_id", "risk_level", "total_outstanding_amount"]].copy()
        customer_daily["stat_date"] = pd.to_datetime(customer_daily["stat_date"], errors="coerce")
        loan = loan.merge(customer_daily, on=["stat_date", "customer_id"], how="left")
    else:
        loan["risk_level"] = pd.NA
        loan["total_outstanding_amount"] = pd.NA
        notes.append("dws_customer_status_snapshot_di 缺少风险或余额字段，risk_level/balance_segment 已降级。")

    customer = load_optional_table(root, "dim", "dim_customer", notes)
    if not customer.empty:
        cust_cols = [col for col in ["customer_id", "province", "risk_level_current"] if col in customer.columns]
        if "customer_id" in cust_cols:
            loan = loan.merge(customer[cust_cols].drop_duplicates("customer_id"), on="customer_id", how="left")
            if "risk_level" in loan and "risk_level_current" in loan:
                loan["risk_level"] = loan["risk_level"].fillna(loan["risk_level_current"])
        else:
            loan["province"] = pd.NA
    else:
        loan["province"] = pd.NA

    vendor = load_optional_table(root, "dim", "dim_vendor", notes)
    if not vendor.empty and {"vendor_id", "vendor_name"}.issubset(vendor.columns):
        loan = loan.merge(vendor[["vendor_id", "vendor_name"]].drop_duplicates("vendor_id"), on="vendor_id", how="left")
    else:
        loan["vendor_name"] = loan["vendor_id"]

    line = load_optional_table(root, "dim", "dim_collection_line", notes)
    if not line.empty and {"line_id", "line_name", "region"}.issubset(line.columns):
        loan = loan.merge(line[["line_id", "line_name", "region"]].drop_duplicates("line_id"), on="line_id", how="left")
    else:
        loan["line_name"] = loan["line_id"]
        loan["region"] = pd.NA

    score = load_optional_table(root, "ods", "ods_postloan_c_score", notes)
    if not score.empty and {"customer_id", "score_date", "score_level"}.issubset(score.columns):
        latest_score = score.sort_values("score_date").drop_duplicates("customer_id", keep="last")
        loan = loan.merge(latest_score[["customer_id", "score_level"]], on="customer_id", how="left")
        loan["score_band"] = loan["score_level"]
    else:
        loan["score_band"] = pd.NA
        notes.append("缺少 score_level，c_score/score_band 维度已降级。")

    attach_process_flags(root, loan, notes)
    attach_reduction_flags(root, loan, notes)
    attach_complaint_flags(root, loan, notes)
    normalize_dimensions(loan)
    return loan


def attach_process_flags(root: Path, fact: pd.DataFrame, notes: list[str]) -> None:
    process = load_optional_table(root, "dws", "dws_collection_process_wide_di", notes)
    required = {
        "stat_date",
        "case_id",
        "action_count",
        "ai_action_count",
        "connected_count",
        "ptp_count",
        "ptp_fulfilled_count",
        "complaint_count",
    }
    if process.empty or not required.issubset(process.columns):
        for col in ["action_count", "ai_action_count", "connected_count", "ptp_count", "ptp_fulfilled_count", "process_complaint_count"]:
            fact[col] = 0
        notes.append("dws_collection_process_wide_di 字段不完整，过程指标证据已降级。")
        return

    process = process[list(required)].copy()
    process["stat_date"] = pd.to_datetime(process["stat_date"], errors="coerce")
    process = process.groupby(["stat_date", "case_id"], as_index=False).sum(numeric_only=True)
    process = process.rename(columns={"complaint_count": "process_complaint_count"})
    joined = fact.merge(process, on=["stat_date", "case_id"], how="left")
    for col in ["action_count", "ai_action_count", "connected_count", "ptp_count", "ptp_fulfilled_count", "process_complaint_count"]:
        fact[col] = pd.to_numeric(joined[col], errors="coerce").fillna(0)


def attach_reduction_flags(root: Path, fact: pd.DataFrame, notes: list[str]) -> None:
    reduction = load_optional_table(root, "ods", "ods_reduction_application", notes)
    if reduction.empty or not {"case_id", "apply_time", "reduction_id"}.issubset(reduction.columns):
        fact["reduction_used"] = False
        notes.append("ods_reduction_application 字段不完整，减免使用证据已降级。")
        return
    reduction = reduction.copy()
    reduction["stat_date"] = pd.to_datetime(reduction["apply_time"], errors="coerce").dt.normalize()
    used = reduction.groupby(["stat_date", "case_id"], as_index=False).agg(reduction_count=("reduction_id", "nunique"))
    joined = fact.merge(used, on=["stat_date", "case_id"], how="left")
    fact["reduction_used"] = pd.to_numeric(joined["reduction_count"], errors="coerce").fillna(0) > 0


def attach_complaint_flags(root: Path, fact: pd.DataFrame, notes: list[str]) -> None:
    complaint = load_optional_table(root, "dwd", "dwd_complaint_detail_di", notes)
    if complaint.empty or not {"case_id", "complaint_date", "complaint_id"}.issubset(complaint.columns):
        fact["complaint_flag"] = False
        notes.append("dwd_complaint_detail_di 字段不完整，投诉证据已降级。")
        return
    complaint = complaint.copy()
    complaint["stat_date"] = pd.to_datetime(complaint["complaint_date"], errors="coerce").dt.normalize()
    counts = complaint.groupby(["stat_date", "case_id"], as_index=False).agg(complaint_count=("complaint_id", "nunique"))
    joined = fact.merge(counts, on=["stat_date", "case_id"], how="left")
    fact["complaint_flag"] = pd.to_numeric(joined["complaint_count"], errors="coerce").fillna(0) > 0


def normalize_dimensions(fact: pd.DataFrame) -> None:
    if "balance_segment" not in fact:
        fact["balance_segment"] = pd.NA
    inferred_balance = pd.Series(
        np.where(pd.to_numeric(fact.get("total_outstanding_amount", 0), errors="coerce").fillna(0) >= 35_000, "HIGH", "NORMAL"),
        index=fact.index,
    )
    fact["balance_segment"] = fact["balance_segment"].fillna(inferred_balance)
    fact["manual_action_count"] = pd.to_numeric(fact["action_count"], errors="coerce").fillna(0) - pd.to_numeric(
        fact["ai_action_count"], errors="coerce"
    ).fillna(0)
    fact["ai_call_coverage"] = np.select(
        [fact["action_count"].eq(0), fact["ai_action_count"].eq(0), fact["ai_action_count"] / fact["action_count"].replace(0, pd.NA) >= 0.5],
        ["NO_ACTION", "NO_AI", "AI_HIGH"],
        default="AI_LOW",
    )
    fact["manual_call_coverage"] = np.select(
        [
            fact["action_count"].eq(0),
            fact["manual_action_count"].eq(0),
            fact["manual_action_count"] / fact["action_count"].replace(0, pd.NA) >= 0.5,
        ],
        ["NO_ACTION", "NO_MANUAL", "MANUAL_HIGH"],
        default="MANUAL_LOW",
    )
    fact["reduction_usage_rate"] = np.where(fact["reduction_used"], "REDUCTION_USED", "NO_REDUCTION")
    fact["ptp_keep_rate"] = np.select(
        [fact["ptp_count"].eq(0), fact["ptp_fulfilled_count"].gt(0)],
        ["NO_PTP", "PTP_KEPT"],
        default="PTP_NOT_KEPT",
    )
    fact["complaint_rate"] = np.where(fact["complaint_flag"], "COMPLAINT", "NO_COMPLAINT")
    for col in [
        "vendor_id",
        "vendor_name",
        "line_id",
        "line_name",
        "collector_id",
        "product_code",
        "channel_code",
        "province",
        "region",
        "dpd_bucket",
        "balance_segment",
        "risk_level",
        "score_band",
    ]:
        if col not in fact:
            fact[col] = pd.NA
        fact[col] = fact[col].fillna("UNKNOWN").astype(str)


def segment_delta(fact: pd.DataFrame, dimension: str, window: WindowSpec) -> pd.DataFrame:
    frame = fact[fact[dimension].notna()].copy()
    frame = frame[~frame[dimension].astype(str).eq("UNKNOWN")]
    if frame[dimension].nunique(dropna=True) < 2:
        return pd.DataFrame()
    frame["period"] = np.select(
        [
            (frame["stat_date"] >= window.baseline_start) & (frame["stat_date"] <= window.baseline_end),
            (frame["stat_date"] >= window.recent_start) & (frame["stat_date"] <= window.recent_end),
        ],
        ["baseline", "recent"],
        default="outside",
    )
    frame = frame[frame["period"].isin(["baseline", "recent"])]
    if frame.empty:
        return pd.DataFrame()

    grouped = frame.groupby(["period", dimension], as_index=False).agg(
        numerator=("repaid_amount_d7", "sum"),
        denominator=("due_amount", "sum"),
        loan_count=("loan_id", "nunique"),
    )
    grouped["value"] = grouped.apply(lambda row: safe_rate(float(row["numerator"]), float(row["denominator"])), axis=1)
    pivot = grouped.pivot(index=dimension, columns="period", values=["numerator", "denominator", "loan_count", "value"]).fillna(0)
    pivot.columns = [f"{metric}_{period}" for metric, period in pivot.columns]
    pivot = pivot.reset_index().rename(columns={dimension: "dimension_value"})
    for col in [
        "numerator_baseline",
        "denominator_baseline",
        "loan_count_baseline",
        "value_baseline",
        "numerator_recent",
        "denominator_recent",
        "loan_count_recent",
        "value_recent",
    ]:
        if col not in pivot:
            pivot[col] = 0.0
    pivot["dimension_name"] = dimension
    pivot["delta"] = pivot["value_recent"] - pivot["value_baseline"]
    return pivot
