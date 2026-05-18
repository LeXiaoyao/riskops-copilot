from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "riskops_cli.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_can_run_and_lists_commands() -> None:
    result = run_cli("--help")

    assert result.returncode == 0, result.stderr
    for command in ["summary", "anomalies", "drivers", "outputs", "render-dashboard", "render-report"]:
        assert command in result.stdout


def test_summary_can_run_and_shows_synthetic_boundary() -> None:
    result = run_cli("summary")

    assert result.returncode == 0, result.stderr
    assert "RiskOps Copilot" in result.stdout
    assert "synthetic data" in result.stdout
    assert "合成数据" in result.stdout
    assert "anomaly 总数" in result.stdout
    assert "dashboard 路径" in result.stdout
    assert "business report 路径" in result.stdout


def test_anomalies_can_run() -> None:
    result = run_cli("anomalies")

    assert result.returncode == 0, result.stderr
    assert "高优先级异常列表" in result.stdout
    assert "metric" in result.stdout or "回收率" in result.stdout
    assert "severity" in result.stdout
    assert "baseline" in result.stdout
    assert "recent" in result.stdout
    assert "relative change" in result.stdout
    assert "recommended next step" in result.stdout


def test_drivers_can_run_and_shows_m1_d7_topic() -> None:
    result = run_cli("drivers")

    assert result.returncode == 0, result.stderr
    assert "M1 D7 回收率下降" in result.stdout
    assert "Top 5 drivers" in result.stdout
    assert "contribution score" in result.stdout
    assert "role / type" in result.stdout
    assert "business interpretation" in result.stdout
    assert "recommended action" in result.stdout
    assert "不是最终根因" in result.stdout
    assert "line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路" in result.stdout
    assert "process evidence 是过程证据" in result.stdout


def test_outputs_can_run_and_marks_file_status() -> None:
    result = run_cli("outputs")

    assert result.returncode == 0, result.stderr
    for path in [
        "outputs/dashboard/dashboard.html",
        "outputs/reports/m4_business_report.md",
        "outputs/reports/m4_business_report.html",
        "outputs/m3/m3_summary.md",
        "outputs/m3/m3_summary.json",
    ]:
        assert path in result.stdout
    assert "exists" in result.stdout or "missing" in result.stdout


def test_render_dashboard_can_run_and_generate_dashboard_html(tmp_path: Path) -> None:
    output_path = tmp_path / "dashboard.html"

    result = run_cli("render-dashboard", "--output", str(output_path))

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "dashboard html" in result.stdout
    assert "anomalies" in result.stdout


def test_render_report_can_run_and_generate_business_report(tmp_path: Path) -> None:
    output_md = tmp_path / "m4_business_report.md"
    output_html = tmp_path / "m4_business_report.html"

    result = run_cli(
        "render-report",
        "--output",
        str(output_md),
        "--html-output",
        str(output_html),
    )

    assert result.returncode == 0, result.stderr
    assert output_md.exists()
    assert output_html.exists()
    assert "business report markdown" in result.stdout
    assert "business report html" in result.stdout


def test_missing_input_file_returns_clear_error(tmp_path: Path) -> None:
    result = run_cli("summary", "--input", str(tmp_path / "missing_m3_summary.json"))

    assert result.returncode == 2
    assert "riskops_cli failed" in result.stderr
    assert "输入文件不存在" in result.stderr
    assert "m3_summary.json" in result.stderr

