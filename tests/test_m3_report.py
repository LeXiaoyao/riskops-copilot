from __future__ import annotations

import json
from pathlib import Path

from riskops.engines.report import M3ReportInputError, build_m3_summary, render_markdown, write_m3_report


def anomaly_payload() -> dict[str, object]:
    return {
        "anomaly_count": 2,
        "severity_counts": {"high": 1, "medium": 1, "low": 0},
        "warnings": [],
        "anomalies": [
            {
                "anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
                "metric_code": "m1_recovery_rate",
                "metric_name_cn": "M1 回收率",
                "anomaly_type": "window_compare",
                "severity": "medium",
                "dimension_name": "overall",
                "dimension_value": "ALL",
                "baseline_value": 0.2,
                "recent_value": 0.15,
                "absolute_change": -0.05,
                "relative_change": -0.25,
                "recent_window": "2026-04-18~2026-05-17",
                "baseline_window": "2026-03-19~2026-04-17",
                "evidence_table": "ads_postloan_dashboard_di",
                "explanation": "M1 回收率下降。",
                "recommended_next_step": "进入 M3-B 归因。",
            },
            {
                "anomaly_id": "M3A-ai_call_coverage-action_type-AI_OUTBOUND",
                "metric_code": "ai_call_coverage",
                "metric_name_cn": "AI 外呼覆盖率",
                "anomaly_type": "window_compare",
                "severity": "high",
                "dimension_name": "action_type",
                "dimension_value": "AI_OUTBOUND",
                "baseline_value": 0.3,
                "recent_value": 0.18,
                "absolute_change": -0.12,
                "relative_change": -0.4,
                "recent_window": "2026-04-18~2026-05-17",
                "baseline_window": "2026-03-19~2026-04-17",
                "evidence_table": "dws_collection_process_wide_di",
                "explanation": "AI 外呼覆盖率下降。",
                "recommended_next_step": "检查 AI 外呼线路容量。",
            },
        ],
    }


def attribution_payload() -> dict[str, object]:
    return {
        "target_metric_code": "recovery_rate_d7",
        "target_anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
        "attribution_count": 1,
        "warnings": [],
        "attributions": [
            {
                "attribution_id": "M3B-recovery_rate_d7-01",
                "target_anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
                "target_metric_code": "recovery_rate_d7",
                "target_metric_name_cn": "D7 回收率",
                "dimension_name": "channel_code",
                "dimension_value": "ECOM",
                "baseline_value": 0.24,
                "recent_value": 0.06,
                "contribution_score": 0.15,
                "contribution_rank": 1,
                "evidence": [
                    {
                        "method": "segment_delta",
                        "baseline_value": 0.24,
                        "recent_value": 0.06,
                        "delta": -0.18,
                        "baseline_loan_count": 100,
                        "recent_loan_count": 120,
                        "baseline_denominator": 100000.0,
                        "recent_denominator": 120000.0,
                        "recent_weight": 0.35,
                    },
                    {
                        "method": "driver_linkage",
                        "metric_code": "ai_call_coverage",
                        "metric_name_cn": "AI 外呼覆盖率",
                        "baseline_value": 0.46,
                        "recent_value": 0.07,
                        "delta": -0.39,
                    },
                ],
                "business_interpretation": "ECOM 分组的回收率下降对整体异常有可量化贡献。",
                "recommended_action": "继续按该维度下钻到供应商、线路和客群组合。",
                "confidence": "medium",
                "notes": ["按 M1 dpd_bucket 过滤后解释 recovery_rate_d7，未重新定义指标口径。"],
            }
        ],
    }


def test_m3_summary_schema_is_stable() -> None:
    summary = build_m3_summary(anomaly_payload(), attribution_payload())
    assert set(summary) == {
        "report_version",
        "source_files",
        "anomaly_overview",
        "high_priority_anomalies",
        "m1_d7_attribution_summary",
        "process_evidence",
        "business_recommendations",
        "data_limitations",
        "next_steps",
    }
    assert summary["m1_d7_attribution_summary"]["primary_driver"]["dimension_name"] == "channel_code"


def test_top_driver_keeps_segment_and_driver_linkage_evidence() -> None:
    summary = build_m3_summary(anomaly_payload(), attribution_payload())
    driver = summary["m1_d7_attribution_summary"]["top_drivers"][0]
    assert driver["segment_evidence"][0]["method"] == "segment_delta"
    assert driver["driver_linkage"][0]["method"] == "driver_linkage"
    assert summary["process_evidence"][0]["metric_code"] == "ai_call_coverage"


def test_markdown_contains_required_sections() -> None:
    markdown = render_markdown(build_m3_summary(anomaly_payload(), attribution_payload()))
    for heading in [
        "## 1. 异常总览",
        "## 2. 高优先级异常列表",
        "## 3. M1 D7 回收率下降归因摘要",
        "## 4. Top 5 drivers",
        "## 5. 每个 driver 的 evidence",
        "## 6. process evidence / driver_linkage",
        "## 7. 业务建议",
        "## 8. 数据局限",
        "## 9. 下一步建议",
    ]:
        assert heading in markdown
    assert "| --- |" not in markdown


def test_write_m3_report_outputs_json_and_markdown(tmp_path: Path) -> None:
    anomaly_path = tmp_path / "anomaly_results.json"
    attribution_path = tmp_path / "attribution_results.json"
    output_json = tmp_path / "m3_summary.json"
    output_md = tmp_path / "m3_summary.md"
    anomaly_path.write_text(json.dumps(anomaly_payload(), ensure_ascii=False), encoding="utf-8")
    attribution_path.write_text(json.dumps(attribution_payload(), ensure_ascii=False), encoding="utf-8")

    write_m3_report(anomaly_path, attribution_path, output_json, output_md)

    assert output_json.exists()
    assert output_md.exists()
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["m1_d7_attribution_summary"]["top_drivers"]


def test_missing_input_file_has_clear_error(tmp_path: Path) -> None:
    attribution_path = tmp_path / "attribution_results.json"
    attribution_path.write_text(json.dumps(attribution_payload(), ensure_ascii=False), encoding="utf-8")

    try:
        write_m3_report(tmp_path / "missing.json", attribution_path, tmp_path / "out.json", tmp_path / "out.md")
    except M3ReportInputError as exc:
        assert "输入文件不存在" in str(exc)
    else:
        raise AssertionError("expected M3ReportInputError")
