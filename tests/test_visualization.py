from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from riskops.engines.visualization import (
    build_anomaly_severity_chart,
    build_capacity_heatmap_chart,
    build_collection_funnel_chart,
    build_complaint_risk_chart,
    build_dpd_structure_chart,
    build_driver_contribution_chart,
    build_reduction_roi_chart,
    build_roi_comparison_chart,
    build_vendor_matrix_chart,
    build_waterfall_chart,
)

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "riskops_cli.py"


def sample_m3_summary() -> dict[str, object]:
    return {
        "high_priority_anomalies": [
            {
                "metric_code": "m1_recovery_rate",
                "metric_name_cn": "M1 回收率",
                "severity": "high",
                "relative_change": -0.58,
            },
            {
                "metric_code": "ai_call_coverage",
                "metric_name_cn": "AI 外呼覆盖率",
                "severity": "medium",
                "relative_change": -0.41,
            },
        ],
        "m1_d7_attribution_summary": {
            "top_drivers": [
                {
                    "dimension_name": "risk_level",
                    "dimension_value": "B",
                    "contribution_score": 0.060159,
                },
                {
                    "dimension_name": "channel_code",
                    "dimension_value": "ECOM",
                    "contribution_score": 0.042,
                },
            ],
        },
    }


def sample_roi_results() -> dict[str, object]:
    return {
        "results": [
            {
                "scenario_id": "increase_ai_call_coverage",
                "estimated_cost": 800.0,
                "estimated_benefit": 30000.0,
                "roi_ratio": 36.5,
            },
            {
                "scenario_id": "increase_manual_capacity",
                "estimated_cost": 8000.0,
                "estimated_benefit": 20000.0,
                "roi_ratio": 1.5,
            },
        ],
    }


def test_build_anomaly_severity_chart_returns_html() -> None:
    html = build_anomaly_severity_chart(sample_m3_summary())

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_driver_contribution_chart_returns_html() -> None:
    html = build_driver_contribution_chart(sample_m3_summary())

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_roi_comparison_chart_returns_html() -> None:
    html = build_roi_comparison_chart(sample_roi_results())

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_collection_funnel_chart_returns_html() -> None:
    html = build_collection_funnel_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_waterfall_chart_returns_html() -> None:
    html = build_waterfall_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_vendor_matrix_chart_returns_html() -> None:
    html = build_vendor_matrix_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_capacity_heatmap_chart_returns_html() -> None:
    html = build_capacity_heatmap_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_dpd_structure_chart_returns_html() -> None:
    html = build_dpd_structure_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_reduction_roi_chart_returns_html() -> None:
    html = build_reduction_roi_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_build_complaint_risk_chart_returns_html() -> None:
    html = build_complaint_risk_chart()

    assert isinstance(html, str)
    assert html
    assert "plotly" in html.lower()


def test_cli_render_charts_can_run(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(CLI), "render-charts", "--output-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "anomaly_severity.html").exists()
    assert (tmp_path / "driver_contribution.html").exists()
    assert (tmp_path / "roi_comparison.html").exists()
    assert (tmp_path / "collection_funnel.html").exists()
    assert (tmp_path / "waterfall.html").exists()
    assert (tmp_path / "vendor_matrix.html").exists()
    assert (tmp_path / "capacity_heatmap.html").exists()
    assert (tmp_path / "dpd_structure.html").exists()
    assert (tmp_path / "reduction_roi.html").exists()
    assert (tmp_path / "complaint_risk.html").exists()
    assert "PASS render-charts" in result.stdout
