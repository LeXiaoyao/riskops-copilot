"""Validate M1 data quality rules."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "synthetic_data"
P4_NAMES = {"customer_name", "id_no", "mobile_no", "bank_card_no", "address"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate M1 RiskOps data quality.")
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    return parser


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_table(root: Path, layer: str, table: str) -> pd.DataFrame:
    for suffix in ["parquet", "csv"]:
        path = root / layer / f"{table}.{suffix}"
        if path.exists():
            return pd.read_parquet(path) if suffix == "parquet" else pd.read_csv(path)
    raise AssertionError(f"missing table file: {layer}/{table}")


def assert_unique(df: pd.DataFrame, pk: str | list[str], table: str) -> None:
    cols = pk if isinstance(pk, list) else [pk]
    duplicated = df.duplicated(cols).sum()
    assert duplicated == 0, f"{table} primary key duplicated: {duplicated}"


def assert_fk(child: pd.DataFrame, child_col: str, parent: pd.DataFrame, parent_col: str, label: str) -> None:
    missing = child.loc[~child[child_col].isin(parent[parent_col]), child_col].nunique()
    assert missing == 0, f"{label} foreign key missing count={missing}"


def iter_existing_tables(root: Path, layers: Iterable[str]) -> Iterable[tuple[str, str, pd.DataFrame]]:
    tables = load_yaml(ROOT / "metadata/tables.yaml")
    for table in tables:
        layer = table["layer"].lower()
        if layer in layers:
            yield layer, table["table_name"], read_table(root, layer, table["table_name"])


def validate_dim_pk(root: Path) -> None:
    for table in load_yaml(ROOT / "metadata/tables.yaml"):
        if table["layer"] == "DIM":
            df = read_table(root, "dim", table["table_name"])
            assert_unique(df, table["primary_key"], table["table_name"])


def validate_foreign_keys(root: Path) -> None:
    customer = read_table(root, "dim", "dim_customer")
    loan = read_table(root, "dim", "dim_loan")
    case = read_table(root, "dim", "dim_case")
    mapping = read_table(root, "dim", "dim_case_loan_mapping")
    vendor = read_table(root, "dim", "dim_vendor")
    line = read_table(root, "dim", "dim_collection_line")
    collector = read_table(root, "dim", "dim_collector")
    plan = read_table(root, "ods", "ods_repayment_plan")
    repay = read_table(root, "ods", "ods_repayment_detail")
    action = read_table(root, "ods", "ods_collection_action")
    note = read_table(root, "ods", "ods_collection_note")
    decision = read_table(root, "ods", "ods_assignment_decision_log")
    complaint = read_table(root, "ods", "ods_complaint")

    assert_fk(loan, "customer_id", customer, "customer_id", "dim_loan.customer_id")
    assert_fk(case, "customer_id", customer, "customer_id", "dim_case.customer_id")
    assert_fk(mapping, "customer_id", customer, "customer_id", "mapping.customer_id")
    assert_fk(mapping, "loan_id", loan, "loan_id", "mapping.loan_id")
    assert_fk(mapping, "case_id", case, "case_id", "mapping.case_id")
    assert_fk(line, "vendor_id", vendor, "vendor_id", "dim_collection_line.vendor_id")
    assert_fk(collector, "line_id", line, "line_id", "dim_collector.line_id")
    assert_fk(plan, "loan_id", loan, "loan_id", "ods_repayment_plan.loan_id")
    assert_fk(repay, "plan_id", plan, "plan_id", "ods_repayment_detail.plan_id")
    assert_fk(action, "case_id", case, "case_id", "ods_collection_action.case_id")
    assert_fk(action, "vendor_id", vendor, "vendor_id", "ods_collection_action.vendor_id")
    assert_fk(action, "line_id", line, "line_id", "ods_collection_action.line_id")
    assert_fk(action, "collector_id", collector, "collector_id", "ods_collection_action.collector_id")
    assert_fk(note, "case_id", case, "case_id", "ods_collection_note.case_id")
    assert_fk(decision, "case_id", case, "case_id", "ods_assignment_decision_log.case_id")
    assert_fk(complaint, "case_id", case, "case_id", "ods_complaint.case_id")


def validate_non_negative_amounts(root: Path) -> None:
    for layer, table, df in iter_existing_tables(root, ["dim", "ods", "dwd", "dws", "ads"]):
        for col in [c for c in df.columns if "amount" in c or c.endswith("_fee") or c.endswith("_principal") or c.endswith("_interest")]:
            bad = (pd.to_numeric(df[col], errors="coerce").fillna(0) < 0).sum()
            assert bad == 0, f"{layer}/{table}.{col} has negative values={bad}"


def validate_dates(root: Path) -> None:
    loan = read_table(root, "dim", "dim_loan")
    repay = read_table(root, "ods", "ods_repayment_detail")
    joined = repay.merge(loan[["loan_id", "disburse_time"]], on="loan_id", how="left")
    bad = (pd.to_datetime(joined["repay_time"]) < pd.to_datetime(joined["disburse_time"])).sum()
    assert bad == 0, f"repay_time before disburse_time count={bad}"

    due = read_table(root, "ods", "ods_repayment_plan")
    bad_due = (pd.to_datetime(due["due_date"]) < pd.to_datetime(loan.set_index("loan_id").loc[due["loan_id"], "disburse_time"]).to_numpy()).sum()
    assert bad_due == 0, f"due_date before disburse_time count={bad_due}"


def validate_privacy(root: Path) -> None:
    columns = load_yaml(ROOT / "metadata/columns.yaml")
    table_layers = {row["table_name"]: row["layer"] for row in load_yaml(ROOT / "metadata/tables.yaml")}
    p4_meta = [row for row in columns if row["privacy_level"] == "P4" and table_layers.get(row["table_name"]) in {"DWD", "DWS", "ADS"}]
    assert p4_meta == [], f"P4 metadata leaked to DWD/DWS/ADS: {p4_meta}"
    for layer, table, df in iter_existing_tables(root, ["dwd", "dws", "ads"]):
        leaked = P4_NAMES.intersection(df.columns)
        assert leaked == set(), f"P4 columns leaked in {layer}/{table}: {sorted(leaked)}"


def validate_rates(root: Path) -> None:
    candidates = ("rate", "share", "pct")
    for layer, table, df in iter_existing_tables(root, ["dws", "ads"]):
        for col in [c for c in df.columns if any(token in c for token in candidates)]:
            values = pd.to_numeric(df[col], errors="coerce").dropna()
            bad = ((values < 0) | (values > 1)).sum()
            assert bad == 0, f"{layer}/{table}.{col} outside [0,1] count={bad}"


def validate_case_mapping(root: Path) -> None:
    case = read_table(root, "dim", "dim_case")
    mapping = read_table(root, "dim", "dim_case_loan_mapping")
    missing = case.loc[~case["case_id"].isin(mapping["case_id"]), "case_id"].nunique()
    assert missing == 0, f"case_id without loan mapping count={missing}"


def validate_snapshots(root: Path) -> None:
    for table in ["ods_loan_daily_snapshot", "ods_case_daily_snapshot", "ods_customer_daily_snapshot"]:
        df = read_table(root, "ods", table)
        counts = df.groupby("stat_date").size()
        zero_days = (counts == 0).sum()
        assert zero_days == 0, f"{table} has zero-count stat_date"
        assert counts.min() > 0, f"{table} minimum daily count is zero"


def validate_raw_secure(root: Path) -> list[str]:
    raw = root / "raw_secure"
    if not raw.exists():
        return []
    files = [p for p in raw.rglob("*") if p.is_file() and p.name != ".gitkeep"]
    if files:
        return [f"raw_secure contains {len(files)} file(s); do not add them to Git."]
    return []


def main() -> int:
    args = build_parser().parse_args()
    checks = [
        ("DQ-001 DIM 主键唯一", validate_dim_pk),
        ("DQ-002 外键可关联", validate_foreign_keys),
        ("DQ-003 金额非负", validate_non_negative_amounts),
        ("DQ-004 日期不穿越", validate_dates),
        ("DQ-005 P4 隔离", validate_privacy),
        ("DQ-006 比率字段范围", validate_rates),
        ("DQ-007 case_id 至少关联 loan_id", validate_case_mapping),
        ("DQ-008 日切表不突降为 0", validate_snapshots),
    ]
    for label, func in checks:
        func(args.data_root)
        print(f"PASS {label}")
    warnings = validate_raw_secure(args.data_root)
    if warnings:
        for warning in warnings:
            print(f"WARN {warning}")
    else:
        print("PASS DQ-009 default raw_secure data files absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
