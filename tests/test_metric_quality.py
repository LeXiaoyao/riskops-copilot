from __future__ import annotations

from pathlib import Path

import pytest

from riskops.metrics.dictionary import load_metric_dictionary
from scripts.validate_metric_quality import (
    DATA_ROOT,
    validate_ads_columns,
    validate_core_not_empty,
    validate_owner_and_lineage,
    validate_ratio_range,
    validate_trends,
)


def ads_is_available() -> bool:
    path = DATA_ROOT / "ads" / "ads_postloan_dashboard_di.parquet"
    if not path.exists():
        return False
    import pandas as pd

    columns = pd.read_parquet(path).columns
    return "m1_recovery_rate" in columns


def test_metric_owner_and_lineage_cover_dictionary() -> None:
    validate_owner_and_lineage(load_metric_dictionary())


@pytest.mark.skipif(not ads_is_available(), reason="ADS metric data has not been built")
def test_ads_metric_quality_checks_pass() -> None:
    metrics = load_metric_dictionary()
    validate_ads_columns(DATA_ROOT)
    validate_ratio_range(metrics, DATA_ROOT)
    validate_core_not_empty(metrics, DATA_ROOT)
    validate_trends(DATA_ROOT)
