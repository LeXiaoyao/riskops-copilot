from __future__ import annotations

from pathlib import Path

import pytest

from riskops.metrics.dictionary import calculate_metric, calculator_registry


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "synthetic_data"


def data_is_available() -> bool:
    return (DATA_ROOT / "dws" / "dws_collection_process_wide_di.parquet").exists() and (
        DATA_ROOT / "dwd" / "dwd_due_plan_detail_di.parquet"
    ).exists()


def test_calculator_registry_exposes_phase1_metrics() -> None:
    registry = calculator_registry()
    assert "m1_recovery_rate" in registry
    assert "connect_rate" in registry
    assert "reduction_roi" in registry
    assert len(registry) == 26


@pytest.mark.skipif(not data_is_available(), reason="synthetic warehouse data has not been built")
def test_calculate_metric_by_metric_code() -> None:
    frame = calculate_metric("connect_rate", DATA_ROOT)
    assert ["stat_date", "connect_rate"] == list(frame.columns)
    assert not frame.empty
    assert frame["connect_rate"].between(0, 1).all()
