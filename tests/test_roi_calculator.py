from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from riskops.engines.model_lab.roi_calculator import (
    DEFAULT_ASSUMPTIONS,
    RESULT_REQUIRED_FIELDS,
    calculate_roi_results,
    load_strategy_eval_results,
    render_roi_markdown,
    write_roi_outputs,
)

ROOT = Path(__file__).resolve().parents[1]
STRATEGY_EVAL = ROOT / "outputs" / "model_lab" / "strategy_eval_results.json"
RUNNER = ROOT / "scripts" / "run_roi_calculator.py"


def _roi_report() -> dict:
    return calculate_roi_results(load_strategy_eval_results(STRATEGY_EVAL))


def _result_by_strategy(report: dict, strategy_type: str) -> dict:
    return next(item for item in report["results"] if item["strategy_type"] == strategy_type)


def test_roi_calculator_generates_five_results() -> None:
    report = _roi_report()

    assert report["scenario_count"] == 5
    assert len(report["results"]) == 5


def test_each_roi_result_contains_required_fields() -> None:
    report = _roi_report()

    for result in report["results"]:
        assert set(RESULT_REQUIRED_FIELDS) <= set(result)


def test_contact_strategy_cost_formula_is_correct() -> None:
    report = _roi_report()
    result = _result_by_strategy(report, "contact_strategy")

    assert result["action_cost"] == DEFAULT_ASSUMPTIONS["assumed_case_base"] * DEFAULT_ASSUMPTIONS["ai_call_unit_cost"]
    assert result["cost_formula"] == "assumed_case_base × ai_call_unit_cost"


def test_settlement_strategy_cost_formula_is_correct() -> None:
    report = _roi_report()
    result = _result_by_strategy(report, "settlement_strategy")
    expected = result["gross_benefit"] * DEFAULT_ASSUMPTIONS["reduction_cost_rate"]

    assert result["action_cost"] == expected
    assert result["cost_formula"] == "gross_benefit × reduction_cost_rate"


def test_roi_ratio_calculation_is_correct() -> None:
    report = _roi_report()
    result = _result_by_strategy(report, "allocation_strategy")
    expected = (result["gross_benefit"] - result["action_cost"]) / result["action_cost"]

    assert result["roi_ratio"] == round(expected, 6)


def test_markdown_contains_demo_disclaimer() -> None:
    markdown = render_roi_markdown(_roi_report())

    assert "Demo Disclaimer" in markdown
    assert "synthetic data only" in markdown
    assert "no real customer data" in markdown
    assert "no real financial conclusion" in markdown
    assert "no real collection action" in markdown
    assert "no SMS / voice / WhatsApp" in markdown
    assert "no LLM decisioning" in markdown


def test_markdown_contains_demo_cost_assumptions() -> None:
    markdown = render_roi_markdown(_roi_report())

    assert "demo cost assumptions" in markdown
    assert "assumed_case_base" in markdown
    assert "unit_recovery_value" in markdown
    assert "reduction_cost_rate" in markdown


def test_missing_strategy_eval_file_returns_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Strategy evaluation results not found"):
        load_strategy_eval_results(tmp_path / "missing_strategy_eval_results.json")


def test_json_and_markdown_outputs_can_generate(tmp_path: Path) -> None:
    output_json = tmp_path / "roi_results.json"
    output_md = tmp_path / "roi_summary.md"
    report = _roi_report()

    write_roi_outputs(report, output_json, output_md)

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["scenario_count"] == 5
    assert "Demo Disclaimer" in output_md.read_text(encoding="utf-8")


def test_run_roi_calculator_cli_can_run(tmp_path: Path) -> None:
    output_json = tmp_path / "roi_results.json"
    output_md = tmp_path / "roi_summary.md"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--strategy-eval",
            str(STRATEGY_EVAL),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "scenario count: 5" in result.stdout
    assert "positive ROI scenarios:" in result.stdout
    assert "PASS ROI calculator" in result.stdout
    assert output_json.exists()
    assert output_md.exists()
