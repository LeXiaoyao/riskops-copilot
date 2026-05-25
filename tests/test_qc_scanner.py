from __future__ import annotations

from pathlib import Path

from riskops.engines.qc import generate_qc_report, scan_batch, scan_text


def test_clean_text_returns_clean() -> None:
    result = scan_text("你赶快还钱，今天处理一下。")

    assert result["risk_level"] == "clean"
    assert result["violation_count"] == 0
    assert result["violations"] == []


def test_violation_detected() -> None:
    result = scan_text("再不还款就起诉你。")

    assert result["violations"]
    assert result["violations"][0]["keyword"] == "起诉你"


def test_high_risk_three_violations() -> None:
    result = scan_text("我是法院，马上起诉你，还会联系你家人。")

    assert result["risk_level"] == "high"
    assert result["violation_count"] >= 3


def test_scan_batch_returns_correct_length() -> None:
    results = scan_batch(["你赶快还钱", "我是公安，联系你家人"])

    assert len(results) == 2


def test_generate_qc_report_creates_file(tmp_path: Path) -> None:
    results = scan_batch(["你赶快还钱", "我是法院，马上起诉你，还会联系你家人。"])
    output_path = tmp_path / "qc_report.md"

    report_path = generate_qc_report(results, output_path)

    assert report_path == str(output_path)
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "## QC 合规扫描报告" in content
    assert "## 违规详情（仅 high 风险）" in content
