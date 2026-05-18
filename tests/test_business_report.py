from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from riskops.engines.report import (
    BusinessReportInputError,
    build_business_report_context,
    render_business_report_html,
    render_business_report_markdown,
    write_business_report,
)

ROOT = Path(__file__).resolve().parents[1]


def sample_summary() -> dict[str, object]:
    return {
        "report_version": "m3-c-v1",
        "demo_disclaimer": "本报告基于 synthetic_data / 合成数据生成，仅用于 Demo 展示，不代表真实业务结论。",
        "anomaly_overview": {
            "anomaly_count": 8,
            "severity_counts": {"high": 6, "medium": 2, "low": 0},
            "baseline_window": "2026-03-19~2026-04-17",
            "recent_window": "2026-04-18~2026-05-17",
        },
        "high_priority_anomalies": [
            {
                "anomaly_id": "M3A-avg_case_per_collector-region-华东",
                "metric_code": "avg_case_per_collector",
                "metric_name_cn": "华东线路人均案量",
                "severity": "high",
                "dimension_name": "region",
                "dimension_value": "华东",
                "baseline_value": 13.54,
                "recent_value": 19.10,
                "absolute_change": 5.56,
                "relative_change": 0.411,
                "explanation": "华东线路人均案量上升。",
                "recommended_next_step": "下钻华东各 line_id。",
            },
            {
                "anomaly_id": "M3A-ai_call_coverage-action_type-AI_OUTBOUND",
                "metric_code": "ai_call_coverage",
                "metric_name_cn": "AI 外呼覆盖率",
                "severity": "high",
                "dimension_name": "action_type",
                "dimension_value": "AI_OUTBOUND",
                "baseline_value": 0.30,
                "recent_value": 0.18,
                "absolute_change": -0.12,
                "relative_change": -0.40,
                "explanation": "AI 外呼覆盖率下降。",
                "recommended_next_step": "检查 AI 外呼覆盖下降原因。",
            },
            {
                "anomaly_id": "M3A-ptp_keep_rate-overall-ALL",
                "metric_code": "ptp_keep_rate",
                "metric_name_cn": "PTP 履约率",
                "severity": "high",
                "dimension_name": "overall",
                "dimension_value": "ALL",
                "baseline_value": 0.50,
                "recent_value": 0.44,
                "absolute_change": -0.06,
                "relative_change": -0.12,
                "explanation": "PTP 履约率下降。",
                "recommended_next_step": "检查 PTP 履约下降原因。",
            },
            {
                "anomaly_id": "M3A-reduction_usage_rate-overall-ALL",
                "metric_code": "reduction_usage_rate",
                "metric_name_cn": "减免使用率",
                "severity": "high",
                "dimension_name": "overall",
                "dimension_value": "ALL",
                "baseline_value": 0.0006,
                "recent_value": 0.0004,
                "absolute_change": -0.0002,
                "relative_change": -0.27,
                "explanation": "减免使用率下降。",
                "recommended_next_step": "检查减免使用不足问题。",
            },
            {
                "anomaly_id": "M3A-complaint_per_10k_cases-template_id-TPL_RISK_NOTICE",
                "metric_code": "complaint_per_10k_cases",
                "metric_name_cn": "万案投诉率",
                "severity": "high",
                "dimension_name": "template_id",
                "dimension_value": "TPL_RISK_NOTICE",
                "baseline_value": 54.2,
                "recent_value": 122.48,
                "absolute_change": 68.28,
                "relative_change": 1.26,
                "explanation": "TPL_RISK_NOTICE 投诉率升高。",
                "recommended_next_step": "对投诉模板做合规复核。",
            },
        ],
        "attribution_target_anomaly": {
            "anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
            "metric_code": "m1_recovery_rate",
            "metric_name_cn": "M1 回收率",
            "severity": "medium",
            "dimension_name": "overall",
            "dimension_value": "ALL",
            "baseline_value": 0.194,
            "recent_value": 0.153,
            "absolute_change": -0.041,
            "relative_change": -0.213,
            "explanation": "M1 回收率下降。",
        },
        "m1_d7_attribution_summary": {
            "target_metric_code": "recovery_rate_d7",
            "target_metric_name_cn": "D7 回收率",
            "target_anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
            "target_anomaly": {
                "anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
                "metric_code": "m1_recovery_rate",
                "metric_name_cn": "M1 回收率",
                "severity": "medium",
                "dimension_name": "overall",
                "dimension_value": "ALL",
                "baseline_value": 0.194,
                "recent_value": 0.153,
                "absolute_change": -0.041,
                "relative_change": -0.213,
                "explanation": "M1 回收率下降。",
            },
            "top_drivers": [
                {
                    "rank": 1,
                    "dimension_name": "channel_code",
                    "dimension_value": "ECOM",
                    "baseline_value": 0.239,
                    "recent_value": 0.063,
                    "contribution_score": 0.153,
                    "business_interpretation": "ECOM 分组的回收率下降对整体异常有可量化贡献。",
                    "recommended_action": "继续下钻到供应商、线路和客群组合。",
                    "confidence": "medium",
                },
                {
                    "rank": 2,
                    "dimension_name": "province",
                    "dimension_value": "山东",
                    "baseline_value": 0.295,
                    "recent_value": 0.127,
                    "contribution_score": 0.065,
                    "business_interpretation": "山东分组回收率下降。",
                    "recommended_action": "复核山东区域供应商和作业线。",
                    "confidence": "medium",
                },
                {
                    "rank": 3,
                    "dimension_name": "score_band",
                    "dimension_value": "D",
                    "baseline_value": 0.178,
                    "recent_value": 0.059,
                    "contribution_score": 0.058,
                    "business_interpretation": "D 客群组内回收表现恶化。",
                    "recommended_action": "检查 D 分客群触达和资源投入。",
                    "confidence": "medium",
                },
                {
                    "rank": 4,
                    "dimension_name": "province",
                    "dimension_value": "上海",
                    "baseline_value": 0.224,
                    "recent_value": 0.072,
                    "contribution_score": 0.044,
                    "business_interpretation": "上海分组回收率下降。",
                    "recommended_action": "复核上海区域供应商和作业线。",
                    "confidence": "medium",
                },
                {
                    "rank": 5,
                    "dimension_name": "score_band",
                    "dimension_value": "A",
                    "baseline_value": 0.364,
                    "recent_value": 0.199,
                    "contribution_score": 0.040,
                    "business_interpretation": "A 客群组内回收表现恶化。",
                    "recommended_action": "检查 A 分客群触达覆盖。",
                    "confidence": "medium",
                },
            ],
        },
        "process_evidence": [
            {
                "driver": "channel_code=ECOM",
                "metric_code": "ai_call_coverage",
                "metric_name_cn": "AI 外呼覆盖率",
                "baseline_value": 0.46,
                "recent_value": 0.07,
                "delta": -0.39,
            },
            {
                "driver": "channel_code=ECOM",
                "metric_code": "ptp_keep_rate",
                "metric_name_cn": "PTP 履约率",
                "baseline_value": 0.50,
                "recent_value": 0.43,
                "delta": -0.07,
            },
            {
                "driver": "channel_code=ECOM",
                "metric_code": "reduction_usage_rate",
                "metric_name_cn": "减免使用率",
                "baseline_value": 0.0006,
                "recent_value": 0.0004,
                "delta": -0.0002,
            },
            {
                "driver": "channel_code=ECOM",
                "metric_code": "complaint_rate",
                "metric_name_cn": "投诉率",
                "baseline_value": 0.005,
                "recent_value": 0.008,
                "delta": 0.003,
            },
        ],
    }


def test_markdown_contains_required_business_sections() -> None:
    markdown = render_business_report_markdown(build_business_report_context(sample_summary()))
    for text in [
        "执行摘要",
        "M1 D7 回收率下降",
        "Top drivers",
        "产能压力",
        "synthetic data / 合成数据",
        "AI 外呼覆盖",
        "PTP 履约",
        "减免使用率",
        "投诉率",
        "line_id 在本项目中表示催收作业线 / 催收单元 / 分案作业队列",
    ]:
        assert text in markdown
    assert "| --- |" not in markdown


def test_write_business_report_outputs_markdown_and_html(tmp_path: Path) -> None:
    input_path = tmp_path / "m3_summary.json"
    output_md = tmp_path / "m4_business_report.md"
    output_html = tmp_path / "m4_business_report.html"
    input_path.write_text(json.dumps(sample_summary(), ensure_ascii=False), encoding="utf-8")

    write_business_report(input_path, output_md, output_html)

    assert output_md.exists()
    assert output_html.exists()
    markdown = output_md.read_text(encoding="utf-8")
    html = output_html.read_text(encoding="utf-8")
    assert "执行摘要" in markdown
    assert "M1 D7 回收率下降" in markdown
    assert "<!DOCTYPE html>" in html
    assert "RiskOps Copilot M4-C" in html


def test_render_business_report_html_uses_markdown_content() -> None:
    markdown = render_business_report_markdown(build_business_report_context(sample_summary()))
    html = render_business_report_html(markdown)
    assert "<h2>1. 执行摘要</h2>" in html
    assert "Top drivers" in html
    assert "synthetic data / 合成数据" in html


def test_missing_input_file_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(BusinessReportInputError) as exc:
        write_business_report(tmp_path / "missing.json", tmp_path / "out.md")
    assert "输入文件不存在" in str(exc.value)
    assert "m3_summary.json" in str(exc.value)


def test_cli_runs_with_explicit_args(tmp_path: Path) -> None:
    input_path = tmp_path / "m3_summary.json"
    output_md = tmp_path / "m4_business_report.md"
    output_html = tmp_path / "m4_business_report.html"
    input_path.write_text(json.dumps(sample_summary(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_business_report.py"),
            "--input",
            str(input_path),
            "--output",
            str(output_md),
            "--html-output",
            str(output_html),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_md.exists()
    assert output_html.exists()
    assert "business report markdown:" in result.stdout


def test_cli_reports_missing_input(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_business_report.py"),
            "--input",
            str(tmp_path / "missing.json"),
            "--output",
            str(tmp_path / "m4_business_report.md"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "render_business_report failed" in result.stderr
    assert "输入文件不存在" in result.stderr
