from __future__ import annotations

from pathlib import Path

import pytest

from riskops.metrics.dictionary import calculate_metric, calculator_registry
from riskops.metrics.calculators.roi import DEFAULT_BASELINE_RECOVERY_WITHOUT_REDUCTION, load_metric_params


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


def test_reduction_roi_metric_params_default_when_config_missing(tmp_path: Path) -> None:
    params = load_metric_params(tmp_path / "missing.yaml")
    assert params["baseline_recovery_without_reduction"] == DEFAULT_BASELINE_RECOVERY_WITHOUT_REDUCTION


def test_reduction_roi_metric_params_loads_configured_baseline(tmp_path: Path) -> None:
    config = tmp_path / "metric_params.yaml"
    config.write_text("reduction_roi:\n  baseline_recovery_without_reduction: 0.79\n", encoding="utf-8")
    params = load_metric_params(config)
    assert params["baseline_recovery_without_reduction"] == 0.79


@pytest.mark.skipif(not data_is_available(), reason="synthetic warehouse data has not been built")
def test_calculate_metric_by_metric_code() -> None:
    frame = calculate_metric("connect_rate", DATA_ROOT)
    assert ["stat_date", "connect_rate"] == list(frame.columns)
    assert not frame.empty
    assert frame["connect_rate"].between(0, 1).all()
