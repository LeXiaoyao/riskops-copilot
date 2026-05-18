"""Load and validate M6-A strategy scenario configs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REQUIRED_SCENARIO_FIELDS = {
    "scenario_id",
    "name",
    "description",
    "strategy_type",
    "target_metric",
    "target_anomaly_id",
    "target_segments",
    "levers",
    "assumptions",
    "constraints",
    "expected_direction",
    "evaluation_notes",
    "compliance_boundary",
}
VALID_STRATEGY_TYPES = {
    "contact_strategy",
    "capacity_strategy",
    "settlement_strategy",
    "allocation_strategy",
    "segmentation_strategy",
}
VALID_EXPECTED_DIRECTIONS = {"improve", "reduce_risk", "monitor"}
REQUIRED_COMPLIANCE_BOUNDARIES = {
    "synthetic_data_only",
    "no_real_customer_data",
    "no_real_collection_action",
    "no_sms_voice_whatsapp",
    "no_llm_decisioning",
}
P4_FIELD_NAMES = {"customer_name", "id_no", "mobile_no", "bank_card_no", "address"}


def load_strategy_scenarios(path: str | Path) -> list[dict[str, Any]]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Strategy scenario config not found: {config_path}")

    try:
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Strategy scenario config is invalid YAML: {config_path}. Error: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"Strategy scenario config must be a YAML mapping: {config_path}")

    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError(f"Strategy scenario config must contain a scenarios list: {config_path}")

    bad_items = [index for index, item in enumerate(scenarios) if not isinstance(item, dict)]
    if bad_items:
        raise ValueError(f"Strategy scenario entries must be mappings. Bad indexes: {bad_items}")

    return scenarios


def validate_strategy_scenarios(scenarios: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, scenario in enumerate(scenarios):
        scenario_id = scenario.get("scenario_id", f"<index:{index}>")
        missing = sorted(REQUIRED_SCENARIO_FIELDS - set(scenario))
        if missing:
            errors.append(f"{scenario_id} missing required fields: {missing}")

        if not isinstance(scenario.get("scenario_id"), str) or not scenario.get("scenario_id"):
            errors.append(f"{scenario_id} scenario_id must be a non-empty string")
        elif scenario["scenario_id"] in seen_ids:
            errors.append(f"{scenario_id} duplicate scenario_id")
        else:
            seen_ids.add(scenario["scenario_id"])

        strategy_type = scenario.get("strategy_type")
        if strategy_type not in VALID_STRATEGY_TYPES:
            errors.append(f"{scenario_id} invalid strategy_type: {strategy_type}")

        expected_direction = scenario.get("expected_direction")
        if expected_direction not in VALID_EXPECTED_DIRECTIONS:
            errors.append(f"{scenario_id} invalid expected_direction: {expected_direction}")

        compliance_boundary = scenario.get("compliance_boundary")
        if not isinstance(compliance_boundary, list):
            errors.append(f"{scenario_id} compliance_boundary must be a list")
        else:
            missing_boundaries = sorted(REQUIRED_COMPLIANCE_BOUNDARIES - set(compliance_boundary))
            if missing_boundaries:
                errors.append(f"{scenario_id} compliance_boundary missing required boundaries: {missing_boundaries}")

        _validate_non_empty_list(scenario, "target_segments", scenario_id, errors)
        _validate_non_empty_list(scenario, "levers", scenario_id, errors)
        _validate_non_empty_list(scenario, "assumptions", scenario_id, errors)
        _validate_non_empty_list(scenario, "constraints", scenario_id, errors)

        leaked_p4 = sorted(P4_FIELD_NAMES.intersection(_flatten_string_values(scenario)))
        if leaked_p4:
            errors.append(f"{scenario_id} contains forbidden P4 field names: {leaked_p4}")

    return errors


def get_strategy_scenario_by_id(scenarios: list[dict[str, Any]], scenario_id: str) -> dict[str, Any] | None:
    for scenario in scenarios:
        if scenario.get("scenario_id") == scenario_id:
            return scenario
    return None


def summarize_strategy_scenarios(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    strategy_type_counts = Counter(str(item.get("strategy_type", "<missing>")) for item in scenarios)
    target_metric_counts = Counter(str(item.get("target_metric", "<missing>")) for item in scenarios)
    return {
        "scenario_count": len(scenarios),
        "strategy_type_counts": dict(sorted(strategy_type_counts.items())),
        "target_metric_counts": dict(sorted(target_metric_counts.items())),
        "scenario_ids": [str(item.get("scenario_id", "<missing>")) for item in scenarios],
    }


def _validate_non_empty_list(scenario: dict[str, Any], field: str, scenario_id: str, errors: list[str]) -> None:
    value = scenario.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{scenario_id} {field} must be a non-empty list")


def _flatten_string_values(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        values: set[str] = set()
        for item in value:
            values.update(_flatten_string_values(item))
        return values
    if isinstance(value, dict):
        values = set()
        for key, item in value.items():
            values.update(_flatten_string_values(key))
            values.update(_flatten_string_values(item))
        return values
    return set()
