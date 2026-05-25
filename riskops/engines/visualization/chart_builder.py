"""Offline Plotly chart builders for RiskOps outputs."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

CHART_WIDTH = 900
CHART_HEIGHT = 420

SEVERITY_COLORS = {
    "high": "#d62728",
    "medium": "#ff7f0e",
    "low": "#8c8c8c",
}


def build_anomaly_severity_chart(m3_summary: dict) -> str:
    rows = [
        item
        for item in _as_list(m3_summary.get("high_priority_anomalies"))
        if isinstance(item, dict) and _is_number(item.get("relative_change"))
    ]
    if not rows:
        return _empty_chart_html("异常信号强度（相对基线）", "缺少 high_priority_anomalies 可视化数据")

    labels = [str(item.get("metric_name_cn") or item.get("metric_code") or "unknown") for item in rows]
    values = [float(item["relative_change"]) for item in rows]
    colors = [SEVERITY_COLORS.get(str(item.get("severity") or "").lower(), SEVERITY_COLORS["low"]) for item in rows]

    fig = go.Figure(
        data=[
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color=colors,
                hovertemplate="%{y}<br>relative_change=%{x:.2%}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="异常信号强度（相对基线）",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="relative_change",
        yaxis_title="metric_name_cn",
        yaxis={"autorange": "reversed"},
        margin={"l": 160, "r": 40, "t": 70, "b": 70},
    )
    fig.update_xaxes(tickformat=".0%")
    return _to_html(fig)


def build_driver_contribution_chart(m3_summary: dict) -> str:
    attribution = m3_summary.get("m1_d7_attribution_summary")
    rows = [
        item
        for item in _as_list(_as_dict(attribution).get("top_drivers"))[:5]
        if isinstance(item, dict) and _is_number(item.get("contribution_score"))
    ]
    if not rows:
        return _empty_chart_html("M1 D7 回收率下降归因 Top5", "缺少 top_drivers 可视化数据")

    labels = [
        "{}={}".format(item.get("dimension_name") or "unknown", item.get("dimension_value") or "unknown")
        for item in rows
    ]
    values = [float(item["contribution_score"]) for item in rows]

    fig = go.Figure(
        data=[
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color="#3b82f6",
                hovertemplate="%{y}<br>contribution_score=%{x:.2%}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="M1 D7 回收率下降归因 Top5",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="contribution_score",
        yaxis_title="driver",
        yaxis={"autorange": "reversed"},
        margin={"l": 170, "r": 40, "t": 70, "b": 70},
    )
    fig.update_xaxes(tickformat=".0%")
    return _to_html(fig)


def build_roi_comparison_chart(roi_results: dict) -> str:
    rows = [item for item in _as_list(roi_results.get("results")) if isinstance(item, dict)]
    valid_rows = [
        item
        for item in rows
        if item.get("scenario_id")
        and _is_number(_first_present(item, "estimated_cost", "action_cost"))
        and _is_number(_first_present(item, "estimated_benefit", "gross_benefit"))
        and _is_number(item.get("roi_ratio"))
    ]
    if not valid_rows:
        return _empty_chart_html("策略情景 ROI 对比", "缺少 ROI results 可视化数据")

    scenario_ids = [str(item["scenario_id"]) for item in valid_rows]
    costs = [float(_first_present(item, "estimated_cost", "action_cost")) for item in valid_rows]
    benefits = [float(_first_present(item, "estimated_benefit", "gross_benefit")) for item in valid_rows]
    roi_ratios = [float(item["roi_ratio"]) for item in valid_rows]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            name="estimated_cost",
            x=scenario_ids,
            y=costs,
            marker_color="#f97316",
            hovertemplate="%{x}<br>estimated_cost=%{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name="estimated_benefit",
            x=scenario_ids,
            y=benefits,
            marker_color="#22c55e",
            hovertemplate="%{x}<br>estimated_benefit=%{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="roi_ratio",
            x=scenario_ids,
            y=roi_ratios,
            mode="lines+markers",
            marker_color="#2563eb",
            line={"width": 3},
            hovertemplate="%{x}<br>roi_ratio=%{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="策略情景 ROI 对比",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        barmode="group",
        xaxis_title="scenario_id",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        margin={"l": 80, "r": 80, "t": 90, "b": 110},
    )
    fig.update_yaxes(title_text="estimated_cost / estimated_benefit", secondary_y=False)
    fig.update_yaxes(title_text="roi_ratio", secondary_y=True)
    return _to_html(fig)


def _empty_chart_html(title: str, message: str) -> str:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 18, "color": "#666666"},
            }
        ],
    )
    return _to_html(fig)


def _to_html(fig: go.Figure) -> str:
    return pio.to_html(fig, full_html=True, include_plotlyjs="cdn")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _first_present(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in item:
            return item[key]
    return None
