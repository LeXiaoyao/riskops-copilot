from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from riskops.engines.model_lab.ml_readiness import (
    assess_ml_readiness,
    render_ml_readiness_report,
    write_ml_readiness_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "synthetic_data"
CLI = ROOT / "scripts" / "riskops_cli.py"


def test_ml_readiness_selects_d7_any_payment_response() -> None:
    readiness = assess_ml_readiness(DATA_DIR)

    assert readiness["recommended_target"] == "d7_any_payment_response"
    assert readiness["data_boundary"] == "synthetic_data_only"
    assert readiness["leakage_guard_summary"]["pii_features_blocked"] is True
    assert readiness["leakage_guard_summary"]["outcome_features_blocked"] is True
    assert {candidate["target_id"] for candidate in readiness["candidates"]} == {
        "d7_any_payment_response",
        "d7_state_recovery_proxy",
        "ptp_fulfillment",
    }


def test_ml_readiness_report_and_outputs_can_generate(tmp_path: Path) -> None:
    readiness = assess_ml_readiness(DATA_DIR)
    report = render_ml_readiness_report(readiness)
    paths = write_ml_readiness_outputs(readiness, tmp_path / "readiness.json", tmp_path / "readiness.md")

    assert "M6-D ML Modeling Readiness" in report
    assert "synthetic data only" in report
    assert Path(paths["readiness_json"]).exists()
    assert Path(paths["readiness_report"]).exists()
    payload = json.loads(Path(paths["readiness_json"]).read_text(encoding="utf-8"))
    assert payload["recommended_target"] == "d7_any_payment_response"


def test_cli_ml_readiness_can_run(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "ml-readiness",
            "--data-dir",
            str(DATA_DIR),
            "--output-json",
            str(tmp_path / "readiness.json"),
            "--output-md",
            str(tmp_path / "readiness.md"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS ML readiness" in result.stdout
    assert "d7_any_payment_response" in result.stdout
    assert (tmp_path / "readiness.json").exists()
    assert (tmp_path / "readiness.md").exists()
