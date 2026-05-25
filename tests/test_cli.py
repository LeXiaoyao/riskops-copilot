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
    for command in [
        "summary",
        "anomalies",
        "drivers",
        "outputs",
        "scenarios",
        "strategy-eval",
        "roi",
        "model-lab",
        "ml-readiness",
        "ml-baseline",
        "qc-scan",
        "render-model-lab",
        "render-dashboard",
        "render-report",
        "render-excel",
        "render-ppt",
    ]:
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
        "outputs/reports/m4_business_report.xlsx",
        "outputs/reports/m4_business_report.pptx",
        "outputs/m3/m3_summary.md",
        "outputs/m3/m3_summary.json",
        "outputs/model_lab/strategy_eval_results.json",
        "outputs/model_lab/strategy_eval_summary.md",
        "outputs/model_lab/roi_results.json",
        "outputs/model_lab/roi_summary.md",
    ]:
        assert path in result.stdout
    assert "exists" in result.stdout or "missing" in result.stdout


def test_scenarios_command_can_run() -> None:
    result = run_cli("scenarios")

    assert result.returncode == 0, result.stderr
    assert "M6-A Strategy Scenarios" in result.stdout
    assert "scenario count" in result.stdout
    assert "increase_ai_call_coverage" in result.stdout
    assert "strategy_type" in result.stdout
    assert "target_metric" in result.stdout
    assert "compliance boundary" in result.stdout


def test_strategy_eval_command_can_run() -> None:
    result = run_cli("strategy-eval")

    assert result.returncode == 0, result.stderr
    assert "M6-B Offline Strategy Evaluation" in result.stdout
    assert "demo estimate" in result.stdout
    assert "estimated_delta" in result.stdout
    assert "confidence" in result.stdout
    assert "不是真实策略决策" in result.stdout


def test_roi_command_can_run_and_shows_demo_cost_assumptions() -> None:
    result = run_cli("roi")

    assert result.returncode == 0, result.stderr
    assert "M6-C ROI Cost-Benefit" in result.stdout
    assert "demo cost assumptions" in result.stdout
    assert "positive ROI scenarios" in result.stdout
    assert "highest ROI scenario" in result.stdout
    assert "gross benefit" in result.stdout
    assert "action cost" in result.stdout
    assert "net benefit" in result.stdout
    assert "roi_ratio" in result.stdout
    assert "no real financial conclusion" in result.stdout


def test_model_lab_command_can_run_and_shows_boundary() -> None:
    result = run_cli("model-lab")

    assert result.returncode == 0, result.stderr
    assert "M6 Model Lab Overview" in result.stdout
    assert "M6-A scenario schema" in result.stdout
    assert "M6-B strategy eval output" in result.stdout
    assert "M6-C ROI output" in result.stdout
    assert "scenario count" in result.stdout
    assert "target metric" in result.stdout
    assert "top recommended scenario" in result.stdout
    assert "synthetic data only" in result.stdout
    assert "no real customer data" in result.stdout


def test_ml_readiness_command_can_run(tmp_path: Path) -> None:
    result = run_cli(
        "ml-readiness",
        "--output-json",
        str(tmp_path / "readiness.json"),
        "--output-md",
        str(tmp_path / "readiness.md"),
    )

    assert result.returncode == 0, result.stderr
    assert "M6-D ML Readiness" in result.stdout
    assert "d7_any_payment_response" in result.stdout
    assert "PASS ML readiness" in result.stdout
    assert (tmp_path / "readiness.json").exists()
    assert (tmp_path / "readiness.md").exists()


def test_ml_baseline_command_can_run(tmp_path: Path) -> None:
    result = run_cli("ml-baseline", "--output-dir", str(tmp_path), "--model", "logistic")

    assert result.returncode == 0, result.stderr
    assert "PASS ML baseline" in result.stdout
    assert "AUC:" in result.stdout
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "feature_importance.csv").exists()


def test_qc_scan_command_can_run() -> None:
    result = run_cli("qc-scan", "--texts", "你赶快还钱", "我是法院，马上起诉你")

    assert result.returncode == 0, result.stderr
    assert "QC 合规关键词扫描" in result.stdout
    assert "risk_level：clean" in result.stdout
    assert "risk_level：medium" in result.stdout
    assert "PASS qc-scan" in result.stdout


def test_render_model_lab_command_can_run_and_generate_m6_outputs(tmp_path: Path) -> None:
    strategy_eval_json = tmp_path / "strategy_eval_results.json"
    strategy_eval_md = tmp_path / "strategy_eval_summary.md"
    roi_json = tmp_path / "roi_results.json"
    roi_md = tmp_path / "roi_summary.md"

    result = run_cli(
        "render-model-lab",
        "--strategy-eval-json",
        str(strategy_eval_json),
        "--strategy-eval-md",
        str(strategy_eval_md),
        "--roi-json",
        str(roi_json),
        "--roi-md",
        str(roi_md),
    )

    assert result.returncode == 0, result.stderr
    assert strategy_eval_json.exists()
    assert strategy_eval_md.exists()
    assert roi_json.exists()
    assert roi_md.exists()
    assert "strategy scenarios validation：PASS" in result.stdout
    assert "PASS model lab render" in result.stdout


def test_m6_cli_outputs_do_not_claim_real_execution_or_finance() -> None:
    for command in ["strategy-eval", "roi", "model-lab"]:
        result = run_cli(command)

        assert result.returncode == 0, result.stderr
        assert "真实策略执行" not in result.stdout
        assert "真实财务结果：" not in result.stdout
        assert "no real customer data" in result.stdout


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
