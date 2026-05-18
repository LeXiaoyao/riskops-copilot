from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from riskops.engines.dashboard import (
    DashboardInputError,
    build_dashboard_context,
    render_dashboard_html,
    write_dashboard,
)

ROOT = Path(__file__).resolve().parents[1]


def sample_summary() -> dict[str, object]:
    return {
        "report_version": "m3-c-v1",
        "demo_disclaimer": "本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。",
        "source_files": {
            "anomaly_results": "outputs/anomalies/anomaly_results.json",
            "attribution_results": "outputs/attribution/attribution_results.json",
        },
        "anomaly_overview": {
            "anomaly_count": 8,
            "severity_counts": {"high": 6, "medium": 2, "low": 0},
            "warnings": [],
            "baseline_window": "2026-03-19~2026-04-17",
            "recent_window": "2026-04-18~2026-05-17",
        },
        "high_priority_anomalies": [
            {
                "anomaly_id": "M3A-avg_case_per_collector-region-华东",
                "metric_code": "avg_case_per_collector",
                "metric_name_cn": "华东线路人均案量",
                "anomaly_type": "spike",
                "severity": "high",
                "dimension_name": "region",
                "dimension_value": "华东",
                "baseline_value": 13.54,
                "recent_value": 19.10,
                "absolute_change": 5.57,
                "relative_change": 0.4113,
                "recent_window": "2026-04-18~2026-05-17",
                "baseline_window": "2026-03-19~2026-04-17",
                "evidence_table": "dws_vendor_line_capacity_di",
                "explanation": "华东线路人均案量上升。",
                "recommended_next_step": "下钻华东各 line_id。",
            },
            {
                "anomaly_id": "M3A-ai_call_coverage-action_type-AI_OUTBOUND",
                "metric_code": "ai_call_coverage",
                "metric_name_cn": "AI 外呼覆盖率",
                "anomaly_type": "window_compare",
                "severity": "high",
                "dimension_name": "action_type",
                "dimension_value": "AI_OUTBOUND",
                "baseline_value": 0.30,
                "recent_value": 0.18,
                "absolute_change": -0.12,
                "relative_change": -0.41,
                "recent_window": "2026-04-18~2026-05-17",
                "baseline_window": "2026-03-19~2026-04-17",
                "evidence_table": "dws_collection_process_wide_di",
                "explanation": "AI 外呼覆盖率下降。",
                "recommended_next_step": "检查 AI 外呼线路容量。",
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
            "attribution_count": 5,
            "warnings": [],
            "primary_driver": None,
            "top_drivers": [
                {
                    "attribution_id": "M3B-recovery_rate_d7-01",
                    "rank": 1,
                    "dimension_name": "channel_code",
                    "dimension_value": "ECOM",
                    "baseline_value": 0.239,
                    "recent_value": 0.063,
                    "contribution_score": 0.1526,
                    "business_interpretation": "ECOM 分组的回收率下降对整体异常有可量化贡献。",
                    "recommended_action": "继续按该维度下钻。",
                    "confidence": "medium",
                },
                {
                    "attribution_id": "M3B-recovery_rate_d7-03",
                    "rank": 3,
                    "dimension_name": "score_band",
                    "dimension_value": "D",
                    "baseline_value": 0.178,
                    "recent_value": 0.059,
                    "contribution_score": 0.0575,
                    "business_interpretation": "D 客群组内回收表现恶化。",
                    "recommended_action": "对该客群单独设定触达策略。",
                    "confidence": "medium",
                },
            ],
        },
        "process_evidence": [
            {
                "attribution_id": "M3B-recovery_rate_d7-01",
                "driver": "channel_code=ECOM",
                "metric_code": "ai_call_coverage",
                "metric_name_cn": "AI 外呼覆盖率",
                "baseline_value": 0.46,
                "recent_value": 0.07,
                "delta": -0.39,
                "method": "driver_linkage",
            },
            {
                "attribution_id": "M3B-recovery_rate_d7-01",
                "driver": "channel_code=ECOM",
                "metric_code": "ptp_keep_rate",
                "metric_name_cn": "PTP 履约率",
                "baseline_value": 0.50,
                "recent_value": 0.43,
                "delta": -0.07,
                "method": "driver_linkage",
            },
            {
                "attribution_id": "M3B-recovery_rate_d7-01",
                "driver": "channel_code=ECOM",
                "metric_code": "reduction_usage_rate",
                "metric_name_cn": "减免使用率",
                "baseline_value": 0.0006,
                "recent_value": 0.0004,
                "delta": -0.0002,
                "method": "driver_linkage",
            },
            {
                "attribution_id": "M3B-recovery_rate_d7-01",
                "driver": "channel_code=ECOM",
                "metric_code": "complaint_rate",
                "metric_name_cn": "投诉率",
                "baseline_value": 0.005,
                "recent_value": 0.008,
                "delta": 0.003,
                "method": "driver_linkage",
            },
        ],
        "business_recommendations": [],
        "data_limitations": [
            {"source": "synthetic_data", "description": "本报告基于 synthetic_data / 合成数据生成。"},
            {"source": "method_boundary", "description": "贡献度为边际贡献，跨维度不可相加。"},
        ],
        "next_steps": [
            {"source": "attribution", "source_id": "M3B-recovery_rate_d7-01", "next_step": "继续按 ECOM 维度下钻。"},
            {"source": "anomaly", "source_id": "M3A-ai_call_coverage-action_type-AI_OUTBOUND", "next_step": "检查 AI 外呼线路容量。"},
        ],
    }


def test_build_context_keeps_raw_numbers() -> None:
    context = build_dashboard_context(sample_summary())
    target = context["attribution_target"]["anomaly"]
    assert target["baseline_value"] == 0.194
    assert target["relative_change"] == -0.213
    drivers = context["top_drivers"]
    assert drivers[0]["contribution_score"] == 0.1526
    assert drivers[0]["driver_role"] == "渠道结构"
    assert drivers[1]["driver_role"] == "客群风险结构"


def test_executive_summary_covers_key_narrative() -> None:
    context = build_dashboard_context(sample_summary())
    lines = context["executive_summary"]
    assert lines, "executive_summary should not be empty"
    joined = "\n".join(lines)
    assert "8 个异常" in joined
    assert "6 个 high" in joined
    assert "2 个 medium" in joined
    assert "D7 回收率" in joined
    # accompaniments present
    assert "AI 外呼覆盖" in joined or "PTP 履约" in joined
    # primary driver hint
    assert "channel_code=ECOM" in joined


def test_top_drivers_have_role_explanation_and_progress() -> None:
    context = build_dashboard_context(sample_summary())
    drivers = context["top_drivers"]
    # ECOM channel
    assert "电商" in drivers[0]["role_explanation"]
    # score_band D (risk layer)
    assert "风险分层" in drivers[1]["role_explanation"]
    # progress pct must be a number, primary driver should hit 100%
    assert drivers[0]["progress_pct"] == 100.0
    assert 0 < drivers[1]["progress_pct"] < 100
    assert context["contribution_max"] == 0.1526


def test_evidence_chains_cover_all_five_categories() -> None:
    context = build_dashboard_context(sample_summary())
    chains = {c["chain_code"]: c for c in context["evidence_chains"]}
    assert set(chains) == {"contact", "fulfill", "tool", "compliance", "capacity"}
    assert chains["contact"]["tone"] == "negative"
    assert chains["fulfill"]["tone"] == "negative"
    assert chains["compliance"]["tone"] == "negative"  # complaint rate rising is bad
    assert chains["capacity"]["tone"] == "negative"  # avg_case_per_collector rising


def test_render_html_contains_required_sections() -> None:
    context = build_dashboard_context(sample_summary())
    html = render_dashboard_html(context)
    assert "<!DOCTYPE html>" in html
    assert "RiskOps Copilot" in html
    assert "M4 Dashboard &amp; Report MVP" in html or "M4 Dashboard & Report MVP" in html
    assert "Demo Disclaimer" in html
    assert "synthetic_data" in html
    # M1 D7 attribution module heading
    assert "M1 D7 回收率下降归因" in html
    # Top drivers detail
    assert "Top 5 drivers" in html
    assert "channel_code" in html
    assert "ECOM" in html
    # Anomaly severity stats
    assert "high 级" in html
    assert "medium 级" in html
    assert "low 级" in html
    # Process evidence groups
    assert "PTP 履约" in html
    assert "AI 外呼覆盖" in html
    assert "减免使用率" in html
    assert "投诉率" in html
    # Capacity signal
    assert "avg_case_per_collector" in html or "华东线路人均案量" in html
    # Roadmap
    assert "M5 TUI" in html
    assert "M6 Model Lab" in html
    assert "M7 Collection QA" in html
    # Readability enhancements
    assert "Executive Summary" in html
    assert "本期一句话结论" in html
    assert "contribution-bar" in html
    assert "evidence-card" in html
    assert "触达证据" in html
    assert "履约证据" in html
    assert "策略工具证据" in html
    assert "合规证据" in html
    assert "产能压力证据" in html
    # Chinese field glossary for the high-priority table
    assert "历史基准" in html
    assert "最近窗口" in html
    assert "相对变化" in html
    # Role explanation surfaced for ECOM channel
    assert "电商" in html


def test_write_dashboard_creates_html(tmp_path: Path) -> None:
    input_path = tmp_path / "m3_summary.json"
    output_path = tmp_path / "dashboard.html"
    input_path.write_text(json.dumps(sample_summary(), ensure_ascii=False), encoding="utf-8")

    write_dashboard(input_path, output_path)

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "Demo Disclaimer" in html
    assert "M1 D7 回收率下降归因" in html


def test_missing_input_raises_clear_error(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(DashboardInputError) as exc:
        write_dashboard(missing, tmp_path / "out.html")
    message = str(exc.value)
    assert "不存在" in message
    assert "m3_summary.json" in message


def test_malformed_input_raises_clear_error(tmp_path: Path) -> None:
    input_path = tmp_path / "m3_summary.json"
    input_path.write_text("not-json", encoding="utf-8")
    with pytest.raises(DashboardInputError) as exc:
        write_dashboard(input_path, tmp_path / "out.html")
    assert "不是合法 JSON" in str(exc.value)


def test_cli_runs_with_explicit_args(tmp_path: Path) -> None:
    input_path = tmp_path / "m3_summary.json"
    output_path = tmp_path / "dashboard.html"
    input_path.write_text(json.dumps(sample_summary(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_dashboard.py"),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "dashboard html:" in result.stdout


def test_cli_reports_missing_input(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_dashboard.py"),
            "--input",
            str(tmp_path / "missing.json"),
            "--output",
            str(tmp_path / "dashboard.html"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "render_dashboard failed" in result.stderr
    assert "不存在" in result.stderr
