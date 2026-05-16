"""Build M1 DWD, DWS, and ADS synthetic warehouse layers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.data.m1_spec import sync_metadata_and_schemas
from riskops.metrics.dictionary import calculate_metric


DATA_ROOT = ROOT / "synthetic_data"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M1 warehouse tables from synthetic DIM/ODS data.")
    parser.add_argument("--input-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--output-format", choices=["csv", "parquet"], default="parquet")
    return parser


def read_table(root: Path, layer: str, table: str) -> pd.DataFrame:
    for suffix in ["parquet", "csv"]:
        path = root / layer / f"{table}.{suffix}"
        if path.exists():
            return pd.read_parquet(path) if suffix == "parquet" else pd.read_csv(path)
    raise FileNotFoundError(f"missing input table: {layer}/{table}")


def write_table(df: pd.DataFrame, root: Path, layer: str, table: str, output_format: str) -> None:
    path = root / layer
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{table}.{output_format}"
    if output_format == "csv":
        df.to_csv(target, index=False)
    else:
        df.to_parquet(target, index=False)


def safe_rate(num: pd.Series | np.ndarray, den: pd.Series | np.ndarray) -> pd.Series:
    numerator = np.asarray(num, dtype=float)
    denominator = np.asarray(den, dtype=float)
    result_values = np.zeros_like(numerator, dtype=float)
    np.divide(numerator, denominator, out=result_values, where=denominator > 0)
    result = pd.Series(result_values)
    return result.clip(0, 1).round(6)


def build_dwd(root: Path) -> dict[str, pd.DataFrame]:
    plan = read_table(root, "ods", "ods_repayment_plan")
    repayment = read_table(root, "ods", "ods_repayment_detail")
    action = read_table(root, "ods", "ods_collection_action")
    flow = read_table(root, "ods", "ods_case_flow")
    complaint = read_table(root, "ods", "ods_complaint")
    loan = read_table(root, "dim", "dim_loan")
    case = read_table(root, "dim", "dim_case")
    mapping = read_table(root, "dim", "dim_case_loan_mapping")

    case_by_loan = mapping.merge(case[["case_id", "initial_dpd_bucket"]], on="case_id", how="left")[["loan_id", "initial_dpd_bucket"]]
    due = plan.merge(loan[["loan_id", "product_code", "channel_code"]], on="loan_id", how="left")
    due = due.merge(case_by_loan.drop_duplicates("loan_id"), on="loan_id", how="left")
    due["stat_date"] = pd.to_datetime(due["due_date"]).dt.date
    due["outstanding_amount"] = due["due_amount"]
    due["dpd_bucket"] = due["initial_dpd_bucket"].fillna("CURRENT")
    dwd_due = due[
        [
            "stat_date",
            "plan_id",
            "loan_id",
            "customer_id",
            "product_code",
            "channel_code",
            "due_date",
            "due_amount",
            "outstanding_amount",
            "dpd_bucket",
        ]
    ].drop_duplicates(["stat_date", "plan_id"])

    repayment["repay_time"] = pd.to_datetime(repayment["repay_time"])
    repayment["repay_date"] = repayment["repay_time"].dt.date
    dwd_repay = repayment[
        ["repay_id", "plan_id", "loan_id", "customer_id", "repay_time", "repay_date", "repay_amount", "repay_status"]
    ].drop_duplicates("repay_id")

    action["action_time"] = pd.to_datetime(action["action_time"])
    action["action_date"] = action["action_time"].dt.date
    dwd_action = action[
        [
            "action_id",
            "case_id",
            "customer_id",
            "vendor_id",
            "line_id",
            "collector_id",
            "action_time",
            "action_date",
            "action_type",
            "template_id",
            "connected_flag",
            "ptp_flag",
            "ptp_fulfilled_flag",
            "ai_outbound_flag",
        ]
    ].drop_duplicates("action_id")

    flow["flow_time"] = pd.to_datetime(flow["flow_time"])
    flow["flow_date"] = flow["flow_time"].dt.date
    dwd_flow = flow[["flow_id", "case_id", "from_status", "to_status", "flow_time", "flow_date", "strategy_id"]].drop_duplicates("flow_id")

    complaint["complaint_time"] = pd.to_datetime(complaint["complaint_time"])
    complaint["complaint_date"] = complaint["complaint_time"].dt.date
    dwd_complaint = complaint[
        [
            "complaint_id",
            "case_id",
            "customer_id",
            "vendor_id",
            "collector_id",
            "template_id",
            "complaint_time",
            "complaint_date",
            "complaint_type",
            "complaint_level",
        ]
    ].drop_duplicates("complaint_id")

    return {
        "dwd_due_plan_detail_di": dwd_due,
        "dwd_repayment_detail_di": dwd_repay,
        "dwd_collection_action_detail_di": dwd_action,
        "dwd_case_flow_detail_di": dwd_flow,
        "dwd_complaint_detail_di": dwd_complaint,
    }


def build_dws(root: Path, dwd: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    case_snapshot = read_table(root, "ods", "ods_case_daily_snapshot")
    customer_snapshot = read_table(root, "ods", "ods_customer_daily_snapshot")
    customer = read_table(root, "dim", "dim_customer")
    case = read_table(root, "dim", "dim_case")
    collector = read_table(root, "dim", "dim_collector")
    line = read_table(root, "dim", "dim_collection_line")
    mapping = read_table(root, "dim", "dim_case_loan_mapping")
    due = dwd["dwd_due_plan_detail_di"].copy()
    repay = dwd["dwd_repayment_detail_di"].copy()
    action = dwd["dwd_collection_action_detail_di"].copy()
    complaint = dwd["dwd_complaint_detail_di"].copy()

    due["due_date"] = pd.to_datetime(due["due_date"])
    repay["repay_time"] = pd.to_datetime(repay["repay_time"])
    repay_d7 = due[["stat_date", "plan_id", "due_date", "due_amount"]].merge(
        repay[["plan_id", "repay_time", "repay_amount"]], on="plan_id", how="left"
    )
    repay_d7["in_d7"] = repay_d7["repay_time"].notna() & (repay_d7["repay_time"] <= repay_d7["due_date"] + pd.Timedelta(days=7))
    repay_sum = repay_d7.assign(repaid_amount_d7=np.where(repay_d7["in_d7"], repay_d7["repay_amount"], 0.0)).groupby(
        "plan_id", as_index=False
    )["repaid_amount_d7"].sum()
    loan_status = due.merge(repay_sum, on="plan_id", how="left")
    loan_status["repaid_amount_d7"] = loan_status["repaid_amount_d7"].fillna(0.0)
    loan_status["recovery_rate_d7"] = safe_rate(loan_status["repaid_amount_d7"], loan_status["due_amount"]).to_numpy()
    loan_status = loan_status[
        ["stat_date", "loan_id", "customer_id", "product_code", "dpd_bucket", "due_amount", "repaid_amount_d7", "recovery_rate_d7"]
    ]

    action_daily = (
        action.groupby(["action_date", "case_id"], as_index=False)
        .agg(
            action_count=("action_id", "count"),
            connected_count=("connected_flag", "sum"),
            ptp_count=("ptp_flag", "sum"),
        )
        .rename(columns={"action_date": "stat_date"})
    )
    repay_by_case = (
        repay.merge(mapping[["case_id", "loan_id"]], on="loan_id", how="inner")
        .groupby(["repay_date", "case_id"], as_index=False)["repay_amount"]
        .sum()
        .rename(columns={"repay_date": "stat_date", "repay_amount": "repaid_amount"})
    )
    case_status = case_snapshot.merge(action_daily, on=["stat_date", "case_id"], how="left").merge(
        repay_by_case, on=["stat_date", "case_id"], how="left"
    )
    for col in ["action_count", "connected_count", "ptp_count", "repaid_amount"]:
        case_status[col] = case_status[col].fillna(0)
    case_status = case_status[
        [
            "stat_date",
            "case_id",
            "customer_id",
            "vendor_id",
            "line_id",
            "collector_id",
            "dpd_bucket",
            "outstanding_amount",
            "action_count",
            "connected_count",
            "ptp_count",
            "repaid_amount",
        ]
    ]

    complaint_daily = complaint.groupby(["complaint_date", "case_id"], as_index=False)["complaint_id"].count().rename(
        columns={"complaint_date": "stat_date", "complaint_id": "complaint_count"}
    )
    process = (
        action.groupby(["action_date", "case_id", "vendor_id", "line_id", "collector_id"], as_index=False)
        .agg(
            action_count=("action_id", "count"),
            ai_action_count=("ai_outbound_flag", "sum"),
            connected_count=("connected_flag", "sum"),
            ptp_count=("ptp_flag", "sum"),
            ptp_fulfilled_count=("ptp_fulfilled_flag", "sum"),
        )
        .rename(columns={"action_date": "stat_date"})
        .merge(complaint_daily, on=["stat_date", "case_id"], how="left")
    )
    process["complaint_count"] = process["complaint_count"].fillna(0).astype(int)
    process["connect_rate"] = safe_rate(process["connected_count"], process["action_count"]).to_numpy()
    process["ptp_fulfillment_rate"] = safe_rate(process["ptp_fulfilled_count"], process["ptp_count"]).to_numpy()
    process["ai_coverage_rate"] = safe_rate(process["ai_action_count"], process["action_count"]).to_numpy()

    capacity = (
        case_snapshot.groupby(["stat_date", "vendor_id", "line_id"], as_index=False)
        .agg(active_case_count=("case_id", "nunique"), active_collector_count=("collector_id", "nunique"))
        .merge(line[["line_id", "region"]], on="line_id", how="left")
    )
    capacity["case_per_collector"] = np.where(
        capacity["active_collector_count"] > 0,
        capacity["active_case_count"] / capacity["active_collector_count"],
        0.0,
    ).round(4)
    capacity = capacity[["stat_date", "vendor_id", "line_id", "region", "active_case_count", "active_collector_count", "case_per_collector"]]

    customer_status = customer_snapshot.copy()
    latest_customer_status = customer_status.sort_values("stat_date").drop_duplicates("customer_id", keep="last")
    latest_date = customer_status["stat_date"].max()
    customer_profile = customer.merge(
        latest_customer_status[["customer_id", "total_outstanding_amount"]], on="customer_id", how="left"
    )
    customer_profile["stat_date"] = latest_date
    customer_profile["total_outstanding_amount"] = customer_profile["total_outstanding_amount"].fillna(0)
    customer_profile = customer_profile[
        [
            "stat_date",
            "customer_id",
            "customer_id_hash",
            "mobile_masked",
            "province",
            "customer_segment",
            "risk_level_current",
            "total_outstanding_amount",
        ]
    ]

    collector_profile = (
        process.groupby(["stat_date", "collector_id"], as_index=False)
        .agg(
            vendor_id=("vendor_id", "first"),
            line_id=("line_id", "first"),
            action_count=("action_count", "sum"),
            connected_count=("connected_count", "sum"),
            complaint_count=("complaint_count", "sum"),
        )
        .merge(collector[["collector_id", "skill_level"]], on="collector_id", how="left")
    )
    collector_profile["connect_rate"] = safe_rate(collector_profile["connected_count"], collector_profile["action_count"]).to_numpy()
    collector_profile = collector_profile[
        ["stat_date", "collector_id", "vendor_id", "line_id", "skill_level", "action_count", "connect_rate", "complaint_count"]
    ]

    tags = customer_status.copy()
    tags["dpd_tag"] = np.where(tags["max_dpd"] <= 30, "M1", np.where(tags["max_dpd"] <= 60, "M2", "M3+"))
    tags["balance_tag"] = np.where(tags["total_outstanding_amount"] >= 35_000, "HIGH", "NORMAL")
    tags["behavior_tag"] = np.where(tags["active_case_count"] > 1, "MULTI_CASE", "SINGLE_CASE")
    tags["touch_tag"] = "TOUCH_PENDING"
    tags["compliance_tag"] = "NORMAL"
    tags["strategy_tag"] = "BASE"
    tags = tags[["stat_date", "customer_id", "dpd_tag", "balance_tag", "behavior_tag", "touch_tag", "compliance_tag", "strategy_tag"]]

    return {
        "dws_loan_status_snapshot_di": loan_status,
        "dws_case_status_snapshot_di": case_status,
        "dws_customer_status_snapshot_di": customer_status,
        "dws_collection_process_wide_di": process,
        "dws_vendor_line_capacity_di": capacity,
        "dws_customer_profile_di": customer_profile,
        "dws_collector_profile_di": collector_profile,
        "dws_customer_postloan_tag_di": tags,
    }


def build_ads(root: Path, dws: dict[str, pd.DataFrame], dwd: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    process = dws["dws_collection_process_wide_di"]
    case_status = dws["dws_case_status_snapshot_di"]
    reduction = read_table(root, "ods", "ods_reduction_application")
    complaint = dwd["dwd_complaint_detail_di"]
    case = read_table(root, "dim", "dim_case")
    max_stat_date = pd.to_datetime(case_status["stat_date"]).dt.date.max()

    metric_codes = [
        "due_account_count",
        "due_loan_count",
        "due_total_amount",
        "collection_entry_rate",
        "recovery_rate_d7",
        "recovery_rate_d15",
        "recovery_rate_d30",
        "m1_recovery_rate",
        "call_coverage_rate",
        "valid_coverage_rate",
        "connect_rate",
        "valid_contact_rate",
        "first_contact_hours",
        "ptp_rate",
        "ptp_keep_rate",
        "avg_call_duration_per_call",
        "avg_call_duration_per_collector",
        "collector_productivity",
        "complaint_rate",
        "complaint_per_10k_cases",
        "risk_phrase_hit_rate",
        "qa_fail_rate",
        "over_frequency_contact_rate",
        "reduction_usage_rate",
        "reduction_recovery_rate",
        "reduction_roi",
    ]
    daily_metrics = [calculate_metric(metric_code, root) for metric_code in metric_codes]
    dashboard = daily_metrics[0]
    for frame in daily_metrics[1:]:
        dashboard = dashboard.merge(frame, on="stat_date", how="outer")
    dashboard = dashboard.sort_values("stat_date").fillna(0)
    dashboard = dashboard[pd.to_datetime(dashboard["stat_date"]).dt.date <= max_stat_date]

    factors = [
        ("CAPACITY_EAST", "华东线路人均案量"),
        ("VENDOR_B_CONNECT", "供应商 B 接通率"),
        ("HIGH_BALANCE_SHARE", "高余额客群占比"),
        ("AI_COVERAGE", "AI 外呼覆盖率"),
        ("REDUCTION_PTP", "减免与 PTP"),
        ("SMS_COMPLAINT", "短信模板投诉"),
    ]
    attribution_rows = []
    for stat_date in dashboard["stat_date"].tail(30):
        for idx, (code, name) in enumerate(factors, start=1):
            attribution_rows.append(
                {
                    "stat_date": stat_date,
                    "factor_code": code,
                    "factor_name": name,
                    "factor_value": float(idx) / 10,
                    "contribution_pct": round(min(1.0, 0.08 + idx * 0.035), 6),
                }
            )
    attribution = pd.DataFrame(attribution_rows)

    vendor_perf = process.groupby(["stat_date", "vendor_id"], as_index=False).agg(
        action_count=("action_count", "sum"),
        called_case_count=("case_id", "nunique"),
        connected_count=("connected_count", "sum"),
        ptp_count=("ptp_count", "sum"),
        ptp_fulfilled_count=("ptp_fulfilled_count", "sum"),
        complaint_count=("complaint_count", "sum"),
    )
    assigned = case_status.groupby(["stat_date", "vendor_id"], as_index=False).agg(assigned_case_count=("case_id", "nunique"))
    vendor_perf = vendor_perf.merge(assigned, on=["stat_date", "vendor_id"], how="left")
    vendor_perf["connect_rate"] = safe_rate(vendor_perf["connected_count"], vendor_perf["action_count"]).to_numpy()
    vendor_perf["ptp_rate"] = safe_rate(vendor_perf["ptp_count"], vendor_perf["connected_count"]).to_numpy()
    vendor_perf["ptp_keep_rate"] = safe_rate(vendor_perf["ptp_fulfilled_count"], vendor_perf["ptp_count"]).to_numpy()
    vendor_perf["complaint_rate"] = safe_rate(vendor_perf["complaint_count"], vendor_perf["assigned_case_count"]).to_numpy()
    vendor_perf["call_coverage_rate"] = safe_rate(vendor_perf["called_case_count"], vendor_perf["assigned_case_count"]).to_numpy()
    vendor_perf = vendor_perf[
        ["stat_date", "vendor_id", "action_count", "call_coverage_rate", "connect_rate", "ptp_rate", "ptp_keep_rate", "complaint_rate"]
    ]

    collector_perf = process.groupby(["stat_date", "collector_id"], as_index=False).agg(
        vendor_id=("vendor_id", "first"),
        action_count=("action_count", "sum"),
        connected_count=("connected_count", "sum"),
        ptp_count=("ptp_count", "sum"),
        ptp_fulfilled_count=("ptp_fulfilled_count", "sum"),
        complaint_count=("complaint_count", "sum"),
    )
    collector_perf["connect_rate"] = safe_rate(collector_perf["connected_count"], collector_perf["action_count"]).to_numpy()
    collector_perf["ptp_keep_rate"] = safe_rate(collector_perf["ptp_fulfilled_count"], collector_perf["ptp_count"]).to_numpy()
    collector_daily = dashboard[
        ["stat_date", "first_contact_hours", "avg_call_duration_per_call", "avg_call_duration_per_collector", "collector_productivity"]
    ]
    collector_perf = collector_perf.merge(collector_daily, on="stat_date", how="left").fillna(0)
    collector_perf = collector_perf[
        [
            "stat_date",
            "collector_id",
            "vendor_id",
            "action_count",
            "connect_rate",
            "ptp_keep_rate",
            "first_contact_hours",
            "avg_call_duration_per_call",
            "avg_call_duration_per_collector",
            "collector_productivity",
            "complaint_count",
        ]
    ]

    reduction["apply_time"] = pd.to_datetime(reduction["apply_time"])
    reduction["stat_date"] = reduction["apply_time"].dt.date
    reduction = reduction[reduction["stat_date"] <= max_stat_date]
    red = reduction.groupby("stat_date", as_index=False).agg(
        reduction_case_count=("case_id", "nunique"),
        approved_reduction_amount=("approved_amount", "sum"),
    )
    reduction_roi = dashboard[["stat_date", "reduction_usage_rate", "reduction_recovery_rate", "reduction_roi"]].merge(
        red, on="stat_date", how="left"
    )
    reduction_roi = reduction_roi.fillna({"reduction_case_count": 0, "approved_reduction_amount": 0})
    reduction_roi["reduction_case_count"] = reduction_roi["reduction_case_count"].astype(int)
    reduction_roi = reduction_roi[
        [
            "stat_date",
            "reduction_case_count",
            "approved_reduction_amount",
            "reduction_usage_rate",
            "reduction_recovery_rate",
            "reduction_roi",
        ]
    ]

    complaint["complaint_date"] = pd.to_datetime(complaint["complaint_date"]).dt.date
    complaint_counts = complaint.groupby("complaint_date", as_index=False)["complaint_id"].count().rename(
        columns={"complaint_date": "stat_date", "complaint_id": "complaint_count"}
    )
    active_cases = case_status.groupby("stat_date", as_index=False)["case_id"].nunique().rename(
        columns={"case_id": "active_case_count"}
    )
    compliance = dashboard[
        [
            "stat_date",
            "complaint_rate",
            "complaint_per_10k_cases",
            "risk_phrase_hit_rate",
            "qa_fail_rate",
            "over_frequency_contact_rate",
        ]
    ].merge(active_cases, on="stat_date", how="left").merge(complaint_counts, on="stat_date", how="left")
    compliance["template_id"] = "ALL"
    compliance = compliance.fillna({"active_case_count": 0, "complaint_count": 0})
    compliance["active_case_count"] = compliance["active_case_count"].astype(int)
    compliance["complaint_count"] = compliance["complaint_count"].astype(int)
    compliance = compliance[
        [
            "stat_date",
            "template_id",
            "active_case_count",
            "complaint_count",
            "complaint_rate",
            "complaint_per_10k_cases",
            "risk_phrase_hit_rate",
            "qa_fail_rate",
            "over_frequency_contact_rate",
        ]
    ]

    return {
        "ads_postloan_dashboard_di": dashboard,
        "ads_recovery_attribution_di": attribution,
        "ads_vendor_performance_di": vendor_perf,
        "ads_collector_performance_di": collector_perf,
        "ads_reduction_roi_di": reduction_roi,
        "ads_compliance_qc_di": compliance,
    }


def main() -> int:
    args = build_parser().parse_args()
    sync_metadata_and_schemas()
    dwd = build_dwd(args.input_root)
    for table, df in dwd.items():
        write_table(df, args.input_root, "dwd", table, args.output_format)
    dws = build_dws(args.input_root, dwd)
    for table, df in dws.items():
        write_table(df, args.input_root, "dws", table, args.output_format)
    ads = build_ads(args.input_root, dws, dwd)
    for table, df in ads.items():
        write_table(df, args.input_root, "ads", table, args.output_format)
    print(f"built dwd_tables={len(dwd)} dws_tables={len(dws)} ads_tables={len(ads)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
