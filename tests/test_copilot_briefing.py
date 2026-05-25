from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from riskops.engines.copilot.briefing_builder import build_copilot_briefing, render_copilot_briefing, write_copilot_briefing


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "riskops_cli.py"
M3_SUMMARY = ROOT / "outputs" / "m3" / "m3_summary.json"
STRATEGY_EVAL = ROOT / "outputs" / "model_lab" / "strategy_eval_results.json"
ROI = ROOT / "outputs" / "model_lab" / "roi_results.json"
ML_METRICS = ROOT / "outputs" / "model_lab" / "ml_baseline" / "metrics.json"
ML_READINESS = ROOT / "outputs" / "model_lab" / "ml_baseline" / "readiness.json"


def test_build_copilot_briefing_uses_existing_outputs() -> None:
    briefing = build_copilot_briefing(M3_SUMMARY, STRATEGY_EVAL, ROI, ML_METRICS, ML_READINESS)

    assert briefing["briefing_type"] == "deterministic_rule_based"
    assert briefing["what_happened"]["anomaly_count"] > 0
    assert briefing["ml_baseline"]["recommended_target"] == "d7_any_payment_response"
    assert "no LLM automatic decisioning" in briefing["boundary"]


def test_render_copilot_briefing_contains_required_sections(tmp_path: Path) -> None:
    briefing = build_copilot_briefing(M3_SUMMARY, STRATEGY_EVAL, ROI, ML_METRICS, ML_READINESS)
    report = render_copilot_briefing(briefing)
    output = write_copilot_briefing(briefing, tmp_path / "briefing.md")

    assert "What Happened" in report
    assert "What Not To Conclude" in report
    assert "does not call an LLM" in report
    assert Path(output).exists()


def test_cli_briefing_can_run(tmp_path: Path) -> None:
    output = tmp_path / "briefing.md"
    result = subprocess.run(
        [sys.executable, str(CLI), "briefing", "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS briefing" in result.stdout
    assert "no LLM automatic decisioning" in result.stdout
    assert output.exists()
