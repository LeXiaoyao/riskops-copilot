from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from riskops.engines.script import mock_approval
from riskops.engines.script.case_context import load_case_context
from riskops.engines.script.frequency_checker import check_frequency
from riskops.engines.script.mock_approval import approve_and_log
from riskops.engines.script.script_engine import generate_script_draft

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "riskops_cli.py"


def test_load_case_context_no_pii() -> None:
    context = load_case_context("CASE-00001")

    assert context["case_id"] == "CASE00000001"
    assert "customer_id_hash" in context
    for pii_field in ["id_no", "mobile_no", "customer_name", "bank_card_no", "address"]:
        assert pii_field not in context


def test_frequency_checker_allows_first_contact() -> None:
    result = check_frequency(
        "CASE-TEST",
        "sms",
        {"recent_sms_count_7d": 0, "_frequency_counts": {"sms": {"today": 0, "week": 0}}},
    )

    assert result["allowed"] is True
    assert result["block_reason"] is None


def test_frequency_checker_blocks_over_limit() -> None:
    result = check_frequency(
        "CASE-TEST",
        "sms",
        {"recent_sms_count_7d": 5, "_frequency_counts": {"sms": {"today": 2, "week": 5}}},
    )

    assert result["allowed"] is False
    assert result["block_reason"]


def test_generate_script_draft_returns_draft() -> None:
    context = load_case_context("CASE-00001")

    draft = generate_script_draft(context["case_id"], "sms", context)

    assert draft["case_id"] == "CASE00000001"
    assert draft["draft_content"]
    assert draft["script_type"]


def test_compliance_scan_triggered() -> None:
    context = load_case_context("CASE-00001")

    draft = generate_script_draft(context["case_id"], "sms", context)

    assert "compliance_scan" in draft
    assert "violation_count" in draft["compliance_scan"]


def test_approve_and_log_writes_file(tmp_path: Path, monkeypatch) -> None:
    log_path = tmp_path / "approval_log.jsonl"
    monkeypatch.setattr(mock_approval, "APPROVAL_LOG_PATH", log_path)
    draft = {
        "draft_id": "DRAFT-TEST",
        "case_id": "CASE-TEST",
        "channel": "sms",
        "draft_content": "测试话术",
        "risk_level": "low",
    }

    result = approve_and_log(draft)

    assert result["status"] == "approved"
    assert log_path.exists()
    assert log_path.read_text(encoding="utf-8").strip()


def test_cli_script_can_run() -> None:
    result = subprocess.run(
        [sys.executable, str(CLI), "script", "--case-id", "CASE-00001", "--channel", "sms"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "=== 话术草稿 ===" in result.stdout or "BLOCKED:" in result.stdout
