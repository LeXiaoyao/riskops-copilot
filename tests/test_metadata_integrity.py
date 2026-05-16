from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TABLES = {
    "dim_customer",
    "dim_loan",
    "dim_case",
    "dim_case_loan_mapping",
    "dim_product",
    "dim_channel",
    "dim_vendor",
    "dim_collection_line",
    "dim_collector",
    "dim_strategy",
    "ods_repayment_plan",
    "ods_repayment_detail",
    "ods_loan_daily_snapshot",
    "ods_case_daily_snapshot",
    "ods_customer_daily_snapshot",
    "ods_case_flow",
    "ods_assignment_decision_log",
    "ods_postloan_c_score",
    "ods_collection_note",
    "ods_collection_action",
    "ods_call_record",
    "ods_sms_send_log",
    "ods_reduction_application",
    "ods_complaint",
    "dwd_due_plan_detail_di",
    "dwd_repayment_detail_di",
    "dwd_collection_action_detail_di",
    "dwd_case_flow_detail_di",
    "dwd_complaint_detail_di",
    "dws_loan_status_snapshot_di",
    "dws_case_status_snapshot_di",
    "dws_customer_status_snapshot_di",
    "dws_collection_process_wide_di",
    "dws_vendor_line_capacity_di",
    "dws_customer_profile_di",
    "dws_collector_profile_di",
    "dws_customer_postloan_tag_di",
    "ads_postloan_dashboard_di",
    "ads_recovery_attribution_di",
    "ads_vendor_performance_di",
    "ads_collector_performance_di",
    "ads_reduction_roi_di",
    "ads_compliance_qc_di",
}


def load_yaml(name: str):
    return yaml.safe_load((ROOT / "metadata" / name).read_text(encoding="utf-8"))


def test_tables_yaml_contains_m1_required_tables() -> None:
    tables = load_yaml("tables.yaml")
    names = {row["table_name"] for row in tables}
    assert REQUIRED_TABLES <= names
    assert len(names) == len(tables)


def test_tables_have_required_metadata_fields() -> None:
    required = {"table_name", "table_name_cn", "layer", "domain", "grain", "primary_key", "description", "owner", "phase"}
    for row in load_yaml("tables.yaml"):
        assert required <= set(row)
        assert row["phase"] == "M1"


def test_columns_have_required_metadata_fields_and_known_tables() -> None:
    tables = {row["table_name"] for row in load_yaml("tables.yaml")}
    required = {
        "table_name",
        "column_name",
        "column_name_cn",
        "data_type",
        "nullable",
        "is_primary_key",
        "privacy_level",
        "description",
    }
    columns = load_yaml("columns.yaml")
    assert columns
    for row in columns:
        assert required <= set(row)
        assert row["table_name"] in tables
        assert row["privacy_level"] in {"P0", "P1", "P2", "P3", "P4"}


def test_schemas_exist_for_all_layers() -> None:
    for name in ["dim.sql", "ods.sql", "dwd.sql", "dws.sql", "ads.sql"]:
        path = ROOT / "schemas" / name
        assert path.is_file()
        assert "CREATE TABLE IF NOT EXISTS" in path.read_text(encoding="utf-8")
