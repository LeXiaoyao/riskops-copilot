from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from riskops.tui.app import (
    HELP_TEXT,
    SLASH_COMMANDS,
    RiskOpsTUIApp,
    read_qc_summary,
    read_script_summary,
    read_vendor_overview,
    run_report_export,
)
from riskops.tui.chat_client import TOOL_SCHEMAS
from riskops.tui.context_loader import load_context
from riskops.tui.tools import get_data_overview, query_anomalies, query_recovery_rate

EXPECTED_SLASH_COMMANDS = {
    "/help",
    "/clear",
    "/context",
    "/summary",
    "/anomaly",
    "/drivers",
    "/roi",
    "/briefing",
    "/model",
    "/qc",
    "/script",
    "/report",
    "/vendor",
}


def test_app_can_instantiate() -> None:
    app = RiskOpsTUIApp()

    assert app is not None


def test_context_loader_returns_string() -> None:
    ctx = load_context()

    assert isinstance(ctx, str)
    assert len(ctx) > 0


def test_slash_commands_recognized() -> None:
    assert SLASH_COMMANDS == EXPECTED_SLASH_COMMANDS


def test_help_text_lists_all_slash_commands() -> None:
    for command in EXPECTED_SLASH_COMMANDS:
        assert command in HELP_TEXT


def test_new_tui_commands_return_strings_with_mock_outputs(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "outputs" / "qc").mkdir(parents=True)
    (tmp_path / "outputs" / "script").mkdir(parents=True)
    (tmp_path / "outputs" / "reports").mkdir(parents=True)
    (tmp_path / "outputs" / "qc" / "qc_summary.md").write_text("# QC\n\n通过", encoding="utf-8")
    (tmp_path / "outputs" / "script" / "script_summary.md").write_text("# Script\n\n建议话术", encoding="utf-8")
    _write_vendor_workbook(tmp_path / "outputs" / "vendor_review.xlsx")

    import riskops.engines.report as report_module

    def fake_write_business_report(input_path: Path, output_md: Path, output_html: Path, output_feishu: Path) -> None:
        output_md.write_text("md", encoding="utf-8")
        output_html.write_text("html", encoding="utf-8")
        output_feishu.write_text("feishu", encoding="utf-8")

    def fake_write_report_with_roi(input_path: Path, output_path: Path, roi_path: Path) -> None:
        output_path.write_text("binary placeholder", encoding="utf-8")

    monkeypatch.setattr(report_module, "write_business_report", fake_write_business_report)
    monkeypatch.setattr(report_module, "write_business_report_excel", fake_write_report_with_roi)
    monkeypatch.setattr(report_module, "write_business_report_ppt", fake_write_report_with_roi)
    monkeypatch.setattr(report_module, "write_business_report_word", fake_write_report_with_roi)

    results = [
        read_qc_summary(tmp_path),
        read_script_summary(tmp_path),
        read_vendor_overview(tmp_path),
        run_report_export(tmp_path),
    ]

    assert all(isinstance(result, str) and result for result in results)
    assert "outputs/qc/qc_summary.md" not in results[0]
    assert "供应商绩效概览" in results[2]
    assert "outputs/reports/m4_business_report.md" in results[3]


def test_new_tui_commands_missing_files_return_friendly_messages(tmp_path: Path) -> None:
    results = [
        read_qc_summary(tmp_path),
        read_script_summary(tmp_path),
        read_vendor_overview(tmp_path),
        run_report_export(tmp_path),
    ]

    assert "未找到 outputs/qc/qc_summary.md，请先跑 run_all.sh" in results[0]
    assert "未找到 outputs/script/script_summary.md，请先跑 run_all.sh" in results[1]
    assert "未找到 outputs/vendor_review.xlsx，请先跑 run_all.sh" in results[2]
    assert "报告导出失败" in results[3]
    assert all("Traceback" not in result for result in results)


def test_tool_schemas_include_local_query_tools() -> None:
    names = {item["function"]["name"] for item in TOOL_SCHEMAS}

    assert "query_recovery_rate" in names
    assert "query_anomalies" in names
    assert "get_data_overview" in names


def test_recovery_rate_tool_returns_series() -> None:
    result = query_recovery_rate(date_start="2026-04-01", date_end="2026-04-07")

    assert result["tool"] == "query_recovery_rate"
    assert result["row_count"] > 0
    assert result["result"]
    assert "recovery_rate_d7" in result["result"][0]


def test_anomaly_tool_can_filter_severity() -> None:
    result = query_anomalies(severity="high")

    assert result["tool"] == "query_anomalies"
    assert all(item["severity"] == "high" for item in result["result"])


def test_data_overview_tool_lists_queryable_files() -> None:
    result = get_data_overview()

    assert result["tool"] == "get_data_overview"
    assert result["row_count"] > 0
    assert result["result"]


def _write_vendor_workbook(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "概览"
    sheet.append(["vendor_id", "recovery_rate", "risk_level"])
    sheet.append(["V001", 0.82, "low"])
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
