"""Validate M2 metric dictionary, calculators, ADS values, and trend fixtures."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.metrics.dictionary import calculator_registry, load_metric_dictionary

DATA_ROOT = ROOT / "synthetic_data"
REQUIRED_FIELDS = {
    "metric_code",
    "metric_name_cn",
    "business_domain",
    "metric_type",
    "numerator",
    "denominator",
    "formula",
    "grain",
    "source_tables",
    "filter_condition",
    "owner",
    "refresh_frequency",
    "version",
    "priority",
    "notes",
    "change_log",
}
VALID_DOMAINS = {"preloan", "midloan", "postloan", "collection", "compliance", "roi", "model"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
ADS_METRIC_TABLES = {
    "ads_postloan_dashboard_di": [
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
    ],
    "ads_vendor_performance_di": ["call_coverage_rate", "connect_rate", "ptp_rate", "ptp_keep_rate", "complaint_rate"],
    "ads_collector_performance_di": [
        "connect_rate",
        "ptp_keep_rate",
        "first_contact_hours",
        "avg_call_duration_per_call",
        "avg_call_duration_per_collector",
        "collector_productivity",
    ],
    "ads_reduction_roi_di": ["reduction_usage_rate", "reduction_recovery_rate", "reduction_roi"],
    "ads_compliance_qc_di": [
        "complaint_rate",
        "complaint_per_10k_cases",
        "risk_phrase_hit_rate",
        "qa_fail_rate",
        "over_frequency_contact_rate",
    ],
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate M2 RiskOps metric quality.")
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    return parser


def read_table(root: Path, layer: str, table: str) -> pd.DataFrame:
    for suffix in ["parquet", "csv"]:
        path = root / layer / f"{table}.{suffix}"
        if path.exists():
            return pd.read_parquet(path) if suffix == "parquet" else pd.read_csv(path)
    raise AssertionError(f"missing table file: {layer}/{table}")


def metric_codes(metrics: Iterable[dict]) -> list[str]:
    return [item["metric_code"] for item in metrics]


def validate_unique_codes(metrics: list[dict]) -> None:
    codes = metric_codes(metrics)
    assert len(codes) == len(set(codes)), "metric_code duplicated"
    bad = [code for code in codes if not re.fullmatch(r"[a-z][a-z0-9_]*", code)]
    assert not bad, f"metric_code must be snake_case: {bad}"


def validate_required_fields(metrics: list[dict]) -> None:
    for item in metrics:
        missing = REQUIRED_FIELDS - set(item)
        assert not missing, f"{item.get('metric_code', '<unknown>')} missing fields: {sorted(missing)}"
        assert item["business_domain"] in VALID_DOMAINS, f"{item['metric_code']} invalid business_domain"
        assert item["priority"] in VALID_PRIORITIES, f"{item['metric_code']} invalid priority"
        assert item["source_tables"], f"{item['metric_code']} source_tables empty"
        assert item["change_log"], f"{item['metric_code']} change_log empty"


def validate_p0_calculators(metrics: list[dict]) -> None:
    registry = calculator_registry()
    missing = [item["metric_code"] for item in metrics if item["priority"] == "P0" and item["metric_code"] not in registry]
    assert not missing, f"P0 metric missing calculator: {missing}"


def validate_p0_source_tables(metrics: list[dict]) -> None:
    missing = [item["metric_code"] for item in metrics if item["priority"] == "P0" and not item["source_tables"]]
    assert not missing, f"P0 metric missing source_tables: {missing}"


def validate_denominator_zero_handling(data_root: Path) -> None:
    registry = calculator_registry()
    for code, func in registry.items():
        frame = func(data_root)
        assert isinstance(frame, pd.DataFrame), f"{code} calculator did not return DataFrame"
        assert code in frame.columns, f"{code} calculator result missing metric column"


def validate_ads_columns(data_root: Path) -> None:
    for table, columns in ADS_METRIC_TABLES.items():
        df = read_table(data_root, "ads", table)
        missing = [col for col in columns if col not in df.columns]
        assert not missing, f"{table} missing metric columns: {missing}"


def validate_ratio_range(metrics: list[dict], data_root: Path) -> None:
    ratio_codes = {item["metric_code"] for item in metrics if item["metric_type"] == "ratio"}
    for table, columns in ADS_METRIC_TABLES.items():
        df = read_table(data_root, "ads", table)
        for col in [c for c in columns if c in ratio_codes and c in df.columns]:
            values = pd.to_numeric(df[col], errors="coerce").dropna()
            bad = ((values < 0) | (values > 1)).sum()
            assert bad == 0, f"{table}.{col} ratio outside [0,1] count={bad}"


def validate_core_not_empty(metrics: list[dict], data_root: Path) -> None:
    dashboard = read_table(data_root, "ads", "ads_postloan_dashboard_di")
    p0_codes = [item["metric_code"] for item in metrics if item["priority"] == "P0" and item["metric_code"] in dashboard.columns]
    for code in p0_codes:
        values = pd.to_numeric(dashboard[code], errors="coerce")
        assert values.notna().any(), f"{code} all null"


def mean_windows(df: pd.DataFrame, value_col: str) -> tuple[float, float]:
    ordered = df.sort_values("stat_date").tail(60)
    assert len(ordered) >= 30, f"{value_col} has fewer than 30 observations"
    recent = pd.to_numeric(ordered.tail(30)[value_col], errors="coerce").mean()
    prior = pd.to_numeric(ordered.iloc[:-30][value_col], errors="coerce").mean()
    return float(prior), float(recent)


def validate_trends(data_root: Path) -> None:
    dashboard = read_table(data_root, "ads", "ads_postloan_dashboard_di")
    prior, recent = mean_windows(dashboard, "m1_recovery_rate")
    assert recent < prior, f"m1_recovery_rate recent mean {recent:.6f} is not below prior mean {prior:.6f}"

    vendor = read_table(data_root, "ads", "ads_vendor_performance_di")
    vendor_b = vendor[vendor["vendor_id"].eq("V_B")]
    prior, recent = mean_windows(vendor_b, "connect_rate")
    assert recent < prior, f"V_B connect_rate recent mean {recent:.6f} is not below prior mean {prior:.6f}"

    reduction = read_table(data_root, "ads", "ads_reduction_roi_di")
    prior, recent = mean_windows(reduction, "reduction_usage_rate")
    assert recent < prior, f"reduction_usage_rate recent mean {recent:.6f} is not below prior mean {prior:.6f}"


def validate_owner_and_lineage(metrics: list[dict]) -> None:
    owners = yaml.safe_load((ROOT / "metadata" / "metric_owner.yaml").read_text(encoding="utf-8"))["owners"]
    lineage = yaml.safe_load((ROOT / "metadata" / "metric_lineage.yaml").read_text(encoding="utf-8"))["metrics"]
    owner_codes = {item["owner"] for item in metrics}
    lineage_codes = {item["metric_code"] for item in lineage}
    codes = set(metric_codes(metrics))
    assert owner_codes <= set(owners), f"metric owner missing metadata: {sorted(owner_codes - set(owners))}"
    assert codes <= lineage_codes, f"metric lineage missing codes: {sorted(codes - lineage_codes)}"


def main() -> int:
    args = build_parser().parse_args()
    metrics = load_metric_dictionary()
    checks = [
        ("MQ-001 metric_code 唯一", lambda: validate_unique_codes(metrics)),
        ("MQ-002 指标字典必填字段完整", lambda: validate_required_fields(metrics)),
        ("MQ-003 P0 指标都有计算函数", lambda: validate_p0_calculators(metrics)),
        ("MQ-004 P0 指标都有 source_tables", lambda: validate_p0_source_tables(metrics)),
        ("MQ-005 分母为 0 时计算不报错", lambda: validate_denominator_zero_handling(args.data_root)),
        ("MQ-006 ADS 指标列完整", lambda: validate_ads_columns(args.data_root)),
        ("MQ-007 比率类指标在 0-1 之间", lambda: validate_ratio_range(metrics, args.data_root)),
        ("MQ-008 核心指标不全为空", lambda: validate_core_not_empty(metrics, args.data_root)),
        ("MQ-009 owner 与血缘元数据完整", lambda: validate_owner_and_lineage(metrics)),
        ("MQ-010 指标趋势夹具符合 M2 验收", lambda: validate_trends(args.data_root)),
    ]
    for label, check in checks:
        check()
        print(f"PASS {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
