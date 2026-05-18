from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from riskops.engines.model_lab.scenario_schema import load_strategy_scenarios
from riskops.engines.model_lab.strategy_evaluator import (
    evaluate_strategy_scenarios,
    load_m3_summary,
    run_strategy_evaluation,
)

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "configs" / "strategy_scenarios.yaml"
M3_SUMMARY = ROOT / "outputs" / "m3" / "m3_summary.json"
RUNNER = ROOT / "scripts" / "run_strategy_eval.py"
REQUIRED_RESULT_FIELDS = {
    "scenario_id",
    "scenario_name",
    "strategy_type",
    "target_metric",
    "target_anomaly_id",
    "baseline_value",
    "scenario_value",
    "estimated_delta",
    "estimated_direction",
    "confidence",
    "impacted_segments",
    "assumptions_used",
    "evidence_links",
    "recommended_action",
    "compliance_boundary",
    "caveats",
}


def test_default_scenarios_can_load() -> None:
    scenarios = load_strategy_scenarios(SCENARIOS)

    assert len(scenarios) == 5


def test_evaluator_generates_five_scenario_results() -> None:
    report = evaluate_strategy_scenarios(load_strategy_scenarios(SCENARIOS), load_m3_summary(M3_SUMMARY))

    assert report["scenario_count"] == 5
    assert len(report["results"]) == 5


def test_each_result_contains_required_fields() -> None:
    report = evaluate_strategy_scenarios(load_strategy_scenarios(SCENARIOS), load_m3_summary(M3_SUMMARY))

    for result in report["results"]:
        assert REQUIRED_RESULT_FIELDS <= set(result)


def test_json_output_can_generate(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"

    run_strategy_evaluation(SCENARIOS, M3_SUMMARY, output_json, output_md)

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["scenario_count"] == 5
    assert len(payload["results"]) == 5


def test_markdown_output_can_generate(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"

    run_strategy_evaluation(SCENARIOS, M3_SUMMARY, output_json, output_md)

    assert output_md.exists()
    assert "Scenario Results" in output_md.read_text(encoding="utf-8")


def test_markdown_contains_demo_disclaimer(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"

    run_strategy_evaluation(SCENARIOS, M3_SUMMARY, output_json, output_md)
    markdown = output_md.read_text(encoding="utf-8")

    assert "Demo Disclaimer" in markdown
    assert "synthetic data only" in markdown
    assert "no real customer data" in markdown
    assert "no real collection action" in markdown
    assert "no SMS / voice / WhatsApp" in markdown
    assert "no LLM decisioning" in markdown


def test_markdown_contains_m1_d7_and_recovery_rate_d7(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"

    run_strategy_evaluation(SCENARIOS, M3_SUMMARY, output_json, output_md)
    markdown = output_md.read_text(encoding="utf-8")

    assert "M1 D7" in markdown
    assert "recovery_rate_d7" in markdown


def test_markdown_explains_line_id_is_not_phone_line(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"

    run_strategy_evaluation(SCENARIOS, M3_SUMMARY, output_json, output_md)
    markdown = output_md.read_text(encoding="utf-8")

    assert "line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路" in markdown


def test_markdown_explains_capacity_pressure_signal_not_root_cause(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"

    run_strategy_evaluation(SCENARIOS, M3_SUMMARY, output_json, output_md)
    markdown = output_md.read_text(encoding="utf-8")

    assert "人均案量是 capacity pressure signal，不是最终根因" in markdown


def test_missing_scenario_file_returns_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Strategy scenario config not found"):
        run_strategy_evaluation(tmp_path / "missing.yaml", M3_SUMMARY, tmp_path / "out.json", tmp_path / "out.md")


def test_missing_m3_summary_file_returns_clear_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="M3 summary not found"):
        run_strategy_evaluation(SCENARIOS, tmp_path / "missing_m3.json", tmp_path / "out.json", tmp_path / "out.md")


def test_run_strategy_eval_cli_can_run(tmp_path: Path) -> None:
    output_json = tmp_path / "strategy_eval_results.json"
    output_md = tmp_path / "strategy_eval_summary.md"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--scenarios",
            str(SCENARIOS),
            "--m3-summary",
            str(M3_SUMMARY),
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
    assert "PASS strategy evaluation" in result.stdout
    assert output_json.exists()
    assert output_md.exists()
