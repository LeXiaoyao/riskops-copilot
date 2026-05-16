from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "synthetic_data"
P4_FIELDS = {"customer_name", "id_no", "mobile_no", "bank_card_no", "address"}


def load_yaml(name: str):
    return yaml.safe_load((ROOT / "metadata" / name).read_text(encoding="utf-8"))


def read_table(layer: str, table: str) -> pd.DataFrame | None:
    for suffix in ["parquet", "csv"]:
        path = DATA_ROOT / layer / f"{table}.{suffix}"
        if path.exists():
            return pd.read_parquet(path) if suffix == "parquet" else pd.read_csv(path)
    return None


def test_privacy_policy_defines_p0_to_p4() -> None:
    policy = load_yaml("privacy_policy.yaml")
    levels = {row["level"] for row in policy["levels"]}
    assert levels == {"P0", "P1", "P2", "P3", "P4"}
    p4 = next(row for row in policy["levels"] if row["level"] == "P4")
    assert p4["warehouse_allowed"] is False
    assert p4["report_allowed"] is False
    assert p4["llm_allowed"] is False


def test_no_p4_metadata_in_dwd_dws_ads() -> None:
    table_layers = {row["table_name"]: row["layer"] for row in load_yaml("tables.yaml")}
    leaked = [
        row
        for row in load_yaml("columns.yaml")
        if row["privacy_level"] == "P4" and table_layers.get(row["table_name"]) in {"DWD", "DWS", "ADS"}
    ]
    assert leaked == []


def test_generated_dwd_dws_ads_do_not_contain_p4_columns() -> None:
    tables = load_yaml("tables.yaml")
    checked = 0
    for table in tables:
        layer = table["layer"].lower()
        if layer not in {"dwd", "dws", "ads"}:
            continue
        df = read_table(layer, table["table_name"])
        if df is None:
            continue
        checked += 1
        assert P4_FIELDS.isdisjoint(df.columns)
    assert checked == 0 or checked == 19
