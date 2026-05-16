from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_data_quality import (
    DATA_ROOT,
    validate_case_mapping,
    validate_dates,
    validate_dim_pk,
    validate_foreign_keys,
    validate_non_negative_amounts,
    validate_privacy,
    validate_rates,
    validate_snapshots,
)


ROOT = Path(__file__).resolve().parents[1]


def data_is_available() -> bool:
    return (DATA_ROOT / "dim" / "dim_customer.parquet").exists() and (
        DATA_ROOT / "ads" / "ads_postloan_dashboard_di.parquet"
    ).exists()


@pytest.mark.skipif(not data_is_available(), reason="synthetic data has not been generated and built")
def test_m1_data_quality_checks_pass() -> None:
    validate_dim_pk(DATA_ROOT)
    validate_foreign_keys(DATA_ROOT)
    validate_non_negative_amounts(DATA_ROOT)
    validate_dates(DATA_ROOT)
    validate_privacy(DATA_ROOT)
    validate_rates(DATA_ROOT)
    validate_case_mapping(DATA_ROOT)
    validate_snapshots(DATA_ROOT)
