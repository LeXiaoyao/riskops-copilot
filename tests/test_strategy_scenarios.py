from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from riskops.engines.model_lab.scenario_schema import (
    REQUIRED_COMPLIANCE_BOUNDARIES,
    VALID_STRATEGY_TYPES,
    load_strategy_scenarios,
    summarize_strategy_scenarios,
    validate_strategy_scenarios,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "strategy_scenarios.yaml"
VALIDATOR = ROOT / "scripts" / "validate_strategy_scenarios.py"


def test_default_strategy_scenarios_can_load() -> None:
    scenarios = load_strategy_scenarios(CONFIG)

    assert scenarios
    assert all("scenario_id" in item for item in scenarios)


def test_strategy_scenario_count_is_at_least_five() -> None:
    scenarios = load_strategy_scenarios(CONFIG)

    assert len(scenarios) >= 5


def test_strategy_scenario_ids_are_unique() -> None:
    scenarios = load_strategy_scenarios(CONFIG)
    scenario_ids = [item["scenario_id"] for item in scenarios]

    assert len(scenario_ids) == len(set(scenario_ids))
    assert validate_strategy_scenarios(scenarios) == []


def test_strategy_types_are_valid() -> None:
    scenarios = load_strategy_scenarios(CONFIG)

    assert {item["strategy_type"] for item in scenarios} <= VALID_STRATEGY_TYPES


def test_compliance_boundary_contains_required_items() -> None:
    scenarios = load_strategy_scenarios(CONFIG)

    for scenario in scenarios:
        assert REQUIRED_COMPLIANCE_BOUNDARIES <= set(scenario["compliance_boundary"])


def test_missing_required_field_returns_clear_error() -> None:
    scenarios = load_strategy_scenarios(CONFIG)
    broken = [dict(scenarios[0])]
    broken[0].pop("target_metric")

    errors = validate_strategy_scenarios(broken)

    assert any("missing required fields" in error for error in errors)
    assert any("target_metric" in error for error in errors)


def test_duplicate_scenario_id_returns_clear_error() -> None:
    scenarios = load_strategy_scenarios(CONFIG)
    broken = [dict(scenarios[0]), dict(scenarios[1])]
    broken[1]["scenario_id"] = broken[0]["scenario_id"]

    errors = validate_strategy_scenarios(broken)

    assert any("duplicate scenario_id" in error for error in errors)


def test_invalid_strategy_type_returns_clear_error() -> None:
    scenarios = load_strategy_scenarios(CONFIG)
    broken = [dict(scenarios[0])]
    broken[0]["strategy_type"] = "real_time_collection_engine"

    errors = validate_strategy_scenarios(broken)

    assert any("invalid strategy_type" in error for error in errors)
    assert any("real_time_collection_engine" in error for error in errors)


def test_validate_strategy_scenarios_cli_can_run() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--config", str(CONFIG)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "scenario count: 5" in result.stdout
    assert "PASS strategy_scenarios validation" in result.stdout


def test_summarize_strategy_scenarios_returns_strategy_type_distribution() -> None:
    scenarios = load_strategy_scenarios(CONFIG)
    summary = summarize_strategy_scenarios(scenarios)

    assert summary["scenario_count"] == len(scenarios)
    assert summary["strategy_type_counts"]["contact_strategy"] == 1
    assert summary["strategy_type_counts"]["capacity_strategy"] == 1
    assert summary["strategy_type_counts"]["settlement_strategy"] == 1
    assert summary["strategy_type_counts"]["allocation_strategy"] == 1
    assert summary["strategy_type_counts"]["segmentation_strategy"] == 1
    assert summary["target_metric_counts"]["recovery_rate_d7"] == 5
