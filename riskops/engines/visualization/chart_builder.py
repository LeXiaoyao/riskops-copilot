"""Offline Plotly chart builders for RiskOps outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

CHART_WIDTH = 900
CHART_HEIGHT = 450
ROOT = Path(__file__).resolve().parents[3]

SEVERITY_COLORS = {
    "high": "#d62728",
    "medium": "#ff7f0e",
    "low": "#8c8c8c",
}

QC_RADAR_DIMENSIONS = ["合规性", "强度", "清晰度", "同理", "完整", "流程"]
QC_RADAR_ALIASES = {
    "合规性": ["合规性", "合规", "合规红线", "overall_compliance_score", "compliance_score"],
    "强度": ["强度", "催收强度", "pressure_score", "intensity_score"],
    "清晰度": ["清晰度", "清晰", "账单事实说明", "金额与日期说明", "clarity_score"],
    "同理": ["同理", "同理心", "情绪控制", "客户异议识别", "empathy_score"],
    "完整": ["完整", "完整性", "开场身份说明", "PTP确认", "结束语规范", "completeness_score"],
    "流程": ["流程", "流程规范", "还款方案引导", "PTP确认", "process_score"],
}


def build_qc_quality_radar_chart(qc_summary: dict) -> str:
    payload = qc_summary or _load_json(ROOT / "outputs" / "qc" / "qc_summary.json") or _mock_qc_summary()
    scores = _extract_qc_radar_scores(payload) or _extract_qc_radar_scores(_mock_qc_summary())

    labels = [*QC_RADAR_DIMENSIONS, QC_RADAR_DIMENSIONS[0]]
    values = [_clip_score(scores[dimension]) for dimension in QC_RADAR_DIMENSIONS]
    values.append(values[0])

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name="最近一期均值",
                line={"color": "#2563eb", "width": 3},
                fillcolor="rgba(37, 99, 235, 0.18)",
                hovertemplate="%{theta}<br>评分=%{r:.1f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="话术质检雷达图（最近一期均值）",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"color": "#0f172a"},
        polar={
            "bgcolor": "#ffffff",
            "radialaxis": {
                "range": [0, 100],
                "tickvals": [0, 20, 40, 60, 80, 100],
                "gridcolor": "#dbeafe",
                "linecolor": "#94a3b8",
            },
            "angularaxis": {"gridcolor": "#dbeafe", "linecolor": "#94a3b8"},
        },
        margin={"l": 90, "r": 90, "t": 80, "b": 60},
        showlegend=False,
    )
    return _to_html(fig)


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


def build_collection_funnel_chart(process_data: dict | None = None) -> str:
    df = _load_dataframe(
        process_data,
        ROOT / "synthetic_data" / "dws" / "dws_collection_process_wide_di.parquet",
    )
    if df.empty or "stat_date" not in df.columns:
        return _empty_chart_html("催收过程漏斗（最近30天均值）", "缺少催收过程宽表数据")

    recent = _recent_days(df, 30)
    if recent.empty:
        return _empty_chart_html("催收过程漏斗（最近30天均值）", "最近30天无催收过程数据")

    daily_rates: list[dict[str, float]] = []
    for _, daily in recent.groupby("stat_date"):
        assigned_count = _case_count(daily)
        action_count = _sum_column(daily, "action_count")
        connected_count = _sum_column(daily, "connected_count")
        ptp_count = _sum_column(daily, "ptp_count")
        ptp_fulfilled_count = _sum_column(daily, "ptp_fulfilled_count")
        touched_count = (
            float((pd.to_numeric(daily.get("action_count"), errors="coerce").fillna(0) > 0).sum())
            if "action_count" in daily
            else assigned_count
        )
        daily_rates.append(
            {
                "分案数": 1.0,
                "首次触达覆盖率": _safe_divide(touched_count, assigned_count),
                "接通率": _safe_divide(connected_count, action_count),
                "有效沟通率": _safe_divide(ptp_count, connected_count),
                "PTP履约率": _safe_divide(ptp_fulfilled_count, ptp_count),
            }
        )

    rate_df = pd.DataFrame(daily_rates).fillna(0)
    steps = ["分案数", "首次触达覆盖率", "接通率", "有效沟通率", "PTP履约率"]
    values = [float(rate_df[step].mean()) for step in steps]

    fig = go.Figure(
        data=[
            go.Funnel(
                y=steps,
                x=values,
                orientation="h",
                marker={"color": ["#64748b", "#2563eb", "#0891b2", "#16a34a", "#f97316"]},
                texttemplate="%{x:.1%}",
                hovertemplate="%{y}<br>转化率=%{x:.2%}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="催收过程漏斗（最近30天均值）",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="转化率",
        margin={"l": 150, "r": 50, "t": 70, "b": 70},
    )
    fig.update_xaxes(tickformat=".0%")
    return _to_html(fig)


def build_waterfall_chart(attribution_data: dict | None = None) -> str:
    payload = attribution_data or _load_json(ROOT / "outputs" / "attribution" / "attribution_results.json")
    rows = _extract_driver_rows(payload)[:5]
    if not rows:
        return _empty_chart_html("M1 D7 回收率归因瀑布图", "缺少 top_drivers 或 attribution 可视化数据")

    baseline = _first_numeric(rows[0], "baseline_value", "baseline")
    current = _first_numeric(rows[0], "recent_value", "current_value", "current")
    if baseline is None:
        baseline = 0.0
    target_delta = (current - baseline) if current is not None else 0.0

    labels = [
        "{}={}".format(
            row.get("dimension_name") or "driver",
            row.get("dimension_value") or row.get("driver") or "unknown",
        )
        for row in rows
    ]
    contributions = []
    for row in rows:
        value = _first_numeric(row, "contribution_amount", "contribution", "contribution_score")
        value = 0.0 if value is None else value
        contributions.append(-abs(value) if target_delta < 0 and value >= 0 else value)

    fig = go.Figure(
        data=[
            go.Waterfall(
                x=["基准值", *labels, "当前值"],
                y=[baseline, *contributions, 0],
                measure=["absolute", *(["relative"] * len(labels)), "total"],
                connector={"line": {"color": "#94a3b8"}},
                increasing={"marker": {"color": "#16a34a"}},
                decreasing={"marker": {"color": "#dc2626"}},
                totals={"marker": {"color": "#2563eb"}},
                hovertemplate="%{x}<br>贡献量=%{y:.2%}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="M1 D7 回收率归因瀑布图",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="归因因子",
        yaxis_title="D7 回收率",
        margin={"l": 80, "r": 40, "t": 70, "b": 120},
    )
    fig.update_yaxes(tickformat=".0%")
    return _to_html(fig)


def build_vendor_matrix_chart(vendor_data: dict | None = None) -> str:
    df = _load_dataframe(
        vendor_data,
        ROOT / "synthetic_data" / "ads" / "ads_vendor_performance_di.parquet",
    )
    if df.empty or "stat_date" not in df.columns or "vendor_id" not in df.columns:
        return _empty_chart_html("供应商表现矩阵（回收 vs 风险）", "缺少供应商表现数据")

    latest = _latest_date_frame(df)
    x_col = _select_column(
        latest,
        ["recovery_contribution", "recovery_contribution_rate", "contribution_rate", "connect_rate"],
    )
    if not x_col:
        return _empty_chart_html("供应商表现矩阵（回收 vs 风险）", "缺少回收贡献率或接通率字段")
    y_col = _select_column(latest, ["complaint_rate"])
    size_col = _select_column(latest, ["case_count", "active_case_count", "action_count"])

    x_values = _numeric_series(latest, x_col)
    if y_col:
        y_values = _numeric_series(latest, y_col)
        y_title = y_col
    elif "ptp_rate" in latest.columns:
        y_values = 1 / _numeric_series(latest, "ptp_rate").replace(0, pd.NA)
        y_values = y_values.replace([float("inf"), -float("inf")], 0).fillna(0)
        y_title = "ptp_rate_inverse"
    else:
        y_values = pd.Series([0.0] * len(latest), index=latest.index)
        y_title = "risk_proxy"

    raw_sizes = (
        _numeric_series(latest, size_col)
        if size_col
        else latest.groupby("vendor_id")["vendor_id"].transform("count").astype(float)
    )
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="markers+text",
                text=latest["vendor_id"].astype(str),
                textposition="top center",
                marker={
                    "size": _scaled_marker_sizes(raw_sizes),
                    "color": y_values,
                    "colorscale": "Reds",
                    "showscale": True,
                    "colorbar": {"title": "风险"},
                    "line": {"width": 1, "color": "#475569"},
                },
                hovertemplate="vendor_id=%{text}<br>回收=%{x:.2%}<br>风险=%{y:.4f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="供应商表现矩阵（回收 vs 风险）",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title=x_col,
        yaxis_title=y_title,
        margin={"l": 80, "r": 90, "t": 70, "b": 80},
    )
    fig.update_xaxes(tickformat=".0%")
    return _to_html(fig)


def build_capacity_heatmap_chart(capacity_data: dict | None = None) -> str:
    df = _load_dataframe(
        capacity_data,
        ROOT / "synthetic_data" / "dws" / "dws_vendor_line_capacity_di.parquet",
    )
    if df.empty or "stat_date" not in df.columns:
        return _empty_chart_html("线路产能热力图（人均案量）", "缺少线路产能数据")

    recent = _recent_days(df, 30)
    y_col = _select_column(recent, ["line_id", "vendor_id"])
    value_col = _select_column(
        recent,
        ["avg_case_per_collector", "case_per_collector", "active_case_per_collector"],
    )
    if not y_col or not value_col:
        return _empty_chart_html("线路产能热力图（人均案量）", "缺少线路或人均案量字段")

    heatmap = recent.copy()
    heatmap["stat_date"] = pd.to_datetime(heatmap["stat_date"]).dt.strftime("%Y-%m-%d")
    pivot = heatmap.pivot_table(index=y_col, columns="stat_date", values=value_col, aggfunc="mean").fillna(0)
    fig = go.Figure(
        data=[
            go.Heatmap(
                x=pivot.columns.tolist(),
                y=pivot.index.astype(str).tolist(),
                z=pivot.values,
                colorscale="YlOrRd",
                colorbar={"title": "人均案量"},
                hovertemplate="日期=%{x}<br>线路=%{y}<br>人均案量=%{z:.2f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="线路产能热力图（人均案量）",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="stat_date",
        yaxis_title=y_col,
        margin={"l": 110, "r": 80, "t": 70, "b": 90},
    )
    return _to_html(fig)


def build_dpd_structure_chart(loan_data: dict | None = None) -> str:
    df = _load_dataframe(
        loan_data,
        ROOT / "synthetic_data" / "dws" / "dws_loan_status_snapshot_di.parquet",
    )
    if df.empty or "stat_date" not in df.columns or "dpd_bucket" not in df.columns:
        return _empty_chart_html("账龄/DPD 结构变化图", "缺少贷款账龄快照数据")

    dated = _with_datetime(df)
    latest_date = dated["stat_date"].max()
    baseline_candidates = dated.loc[dated["stat_date"] <= latest_date - pd.Timedelta(days=30), "stat_date"]
    baseline_date = baseline_candidates.max() if not baseline_candidates.empty else dated["stat_date"].min()
    current = dated[dated["stat_date"] == latest_date]
    baseline = dated[dated["stat_date"] == baseline_date]
    buckets = _ordered_dpd_buckets(set(current["dpd_bucket"].astype(str)) | set(baseline["dpd_bucket"].astype(str)))
    current_counts = _bucket_counts(current, buckets)
    baseline_counts = _bucket_counts(baseline, buckets)
    current_rates = _bucket_rates(current_counts)
    baseline_rates = _bucket_rates(baseline_counts)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="当前期",
            x=buckets,
            y=current_rates,
            customdata=current_counts,
            marker_color="#2563eb",
            hovertemplate="%{x}<br>占比=%{y:.2%}<br>案件数=%{customdata}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="基准期",
            x=buckets,
            y=baseline_rates,
            customdata=baseline_counts,
            marker_color="#94a3b8",
            hovertemplate="%{x}<br>占比=%{y:.2%}<br>案件数=%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(
        title="账龄/DPD 结构变化图",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        barmode="group",
        xaxis_title="dpd_bucket",
        yaxis_title="案件占比",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        margin={"l": 80, "r": 40, "t": 90, "b": 80},
    )
    fig.update_yaxes(tickformat=".0%")
    return _to_html(fig)


def build_reduction_roi_chart(roi_data: dict | None = None) -> str:
    df = _load_dataframe(
        roi_data,
        ROOT / "synthetic_data" / "ads" / "ads_reduction_roi_di.parquet",
    )
    if df.empty or "stat_date" not in df.columns:
        return _empty_chart_html("减免 ROI 趋势图", "缺少减免 ROI 数据")

    dated = _with_datetime(df).sort_values("stat_date")
    amount_col = _select_column(dated, ["approved_reduction_amount", "reduction_amount", "discount_amount"])
    ratio_col = _select_column(
        dated,
        ["recovery_lift_rate", "recovery_uplift_rate", "reduction_roi", "roi", "reduction_recovery_rate"],
    )
    if not amount_col and not ratio_col:
        return _empty_chart_html("减免 ROI 趋势图", "缺少减免金额或 ROI 字段")

    x_values = dated["stat_date"].dt.strftime("%Y-%m-%d")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if amount_col:
        fig.add_trace(
            go.Scatter(
                name=amount_col,
                x=x_values,
                y=_numeric_series(dated, amount_col),
                mode="lines",
                line={"color": "#f97316", "width": 3},
                hovertemplate="%{x}<br>减免金额=%{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )
    if ratio_col:
        fig.add_trace(
            go.Scatter(
                name=ratio_col,
                x=x_values,
                y=_numeric_series(dated, ratio_col),
                mode="lines+markers",
                line={"color": "#2563eb", "width": 2},
                marker={"size": 5},
                hovertemplate="%{x}<br>ROI/提升率=%{y:.4f}<extra></extra>",
            ),
            secondary_y=True,
        )
    fig.update_layout(
        title="减免 ROI 趋势图",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="stat_date",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        margin={"l": 80, "r": 80, "t": 90, "b": 80},
    )
    fig.update_yaxes(title_text=amount_col or "reduction_amount", secondary_y=False)
    fig.update_yaxes(title_text=ratio_col or "roi", secondary_y=True)
    return _to_html(fig)


def build_complaint_risk_chart(vendor_data: dict | None = None) -> str:
    df = _load_dataframe(
        vendor_data,
        ROOT / "synthetic_data" / "ads" / "ads_compliance_qc_di.parquet",
    )
    if df.empty:
        df = _load_dataframe(None, ROOT / "synthetic_data" / "ads" / "ads_vendor_performance_di.parquet")
    if df.empty:
        return _empty_chart_html("供应商/线路投诉风险分布", "缺少合规质检或供应商表现数据")

    latest = _latest_date_frame(df) if "stat_date" in df.columns else df.copy()
    group_col = _select_column(latest, ["vendor_id", "line_id", "template_id"])
    if not group_col:
        return _empty_chart_html("供应商/线路投诉风险分布", "缺少供应商、线路或质检维度字段")

    risk_cols = [
        col
        for col in ["complaint_rate", "risk_phrase_hit_rate", "qa_fail_rate", "over_frequency_contact_rate"]
        if col in latest.columns
    ]
    if risk_cols:
        latest = latest.copy()
        latest["risk_score"] = sum(_numeric_series(latest, col) for col in risk_cols)
    elif "complaint_per_10k_cases" in latest.columns:
        latest = latest.copy()
        latest["risk_score"] = _numeric_series(latest, "complaint_per_10k_cases")
    else:
        latest = latest.copy()
        latest["risk_score"] = 0.0

    grouped = latest.groupby(group_col, as_index=False)["risk_score"].mean().sort_values("risk_score", ascending=False)
    threshold = float(grouped["risk_score"].median()) if not grouped.empty else 0.0
    colors = ["#dc2626" if value >= threshold and value > 0 else "#2563eb" for value in grouped["risk_score"]]

    fig = go.Figure(
        data=[
            go.Bar(
                x=grouped["risk_score"],
                y=grouped[group_col].astype(str),
                orientation="h",
                marker_color=colors,
                hovertemplate="%{y}<br>风险分=%{x:.4f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title="供应商/线路投诉风险分布",
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="risk_score",
        yaxis_title=group_col,
        yaxis={"autorange": "reversed"},
        margin={"l": 150, "r": 40, "t": 70, "b": 80},
    )
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


def _extract_qc_radar_scores(payload: dict[str, Any]) -> dict[str, float]:
    records = _latest_qc_records(payload)
    values_by_dimension: dict[str, list[float]] = {dimension: [] for dimension in QC_RADAR_DIMENSIONS}
    for record in records:
        source = _flatten_qc_score_record(record)
        for dimension, aliases in QC_RADAR_ALIASES.items():
            values = [_to_score_value(source.get(alias)) for alias in aliases]
            valid_values = [value for value in values if value is not None]
            if valid_values:
                values_by_dimension[dimension].append(sum(valid_values) / len(valid_values))

    scores = {
        dimension: sum(values) / len(values)
        for dimension, values in values_by_dimension.items()
        if values
    }
    if len(scores) != len(QC_RADAR_DIMENSIONS):
        return {}
    return scores


def _latest_qc_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ["recent_period", "latest_period", "latest", "current", "dimension_means", "scores", "dimensions"]:
        value = payload.get(key)
        if isinstance(value, dict):
            return [value]

    for key in ["summary", "quality_summary"]:
        value = payload.get(key)
        if isinstance(value, dict):
            records = _latest_qc_records(value)
            if records:
                return records

    rows = payload.get("rows") or payload.get("data") or payload.get("records") or payload.get("results")
    if isinstance(rows, list):
        dict_rows = [row for row in rows if isinstance(row, dict)]
        if not dict_rows:
            return []
        date_key = _select_qc_date_key(dict_rows)
        if not date_key:
            return dict_rows
        dated = pd.DataFrame(dict_rows)
        parsed_dates = pd.to_datetime(dated[date_key], errors="coerce")
        if parsed_dates.notna().any():
            latest_date = parsed_dates.max()
            return [
                row
                for row, parsed_date in zip(dict_rows, parsed_dates, strict=False)
                if pd.notna(parsed_date) and parsed_date == latest_date
            ]
        return dict_rows

    return [payload] if payload else []


def _select_qc_date_key(records: list[dict[str, Any]]) -> str | None:
    for key in ["stat_date", "score_date", "batch_date", "period", "date"]:
        if any(key in record for record in records):
            return key
    return None


def _flatten_qc_score_record(record: dict[str, Any]) -> dict[str, Any]:
    source: dict[str, Any] = {}
    for key in ["dimensions", "dimension_scores", "avg_scores", "quality_scores", "scores"]:
        value = record.get(key)
        if isinstance(value, dict):
            source.update(value)
    source.update(record)
    return source


def _to_score_value(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _clip_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def _mock_qc_summary() -> dict[str, Any]:
    return {
        "latest_period": {
            "合规性": 84,
            "强度": 68,
            "清晰度": 78,
            "同理": 74,
            "完整": 80,
            "流程": 76,
        }
    }


def _first_present(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in item:
            return item[key]
    return None


def _load_dataframe(data: dict | None, default_path: Path) -> pd.DataFrame:
    if data:
        rows = data.get("rows") or data.get("data") or data.get("records")
        if isinstance(rows, list):
            return pd.DataFrame(rows)
    if not default_path.exists():
        return pd.DataFrame()
    return pd.read_parquet(default_path)


def _load_json(default_path: Path) -> dict[str, Any]:
    if not default_path.exists():
        return {}
    payload = json.loads(default_path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _with_datetime(df: pd.DataFrame) -> pd.DataFrame:
    dated = df.copy()
    dated["stat_date"] = pd.to_datetime(dated["stat_date"], errors="coerce")
    return dated.dropna(subset=["stat_date"])


def _recent_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    dated = _with_datetime(df)
    if dated.empty:
        return dated
    latest_date = dated["stat_date"].max()
    return dated[dated["stat_date"] >= latest_date - pd.Timedelta(days=days - 1)]


def _latest_date_frame(df: pd.DataFrame) -> pd.DataFrame:
    dated = _with_datetime(df)
    if dated.empty:
        return pd.DataFrame()
    latest_date = dated["stat_date"].max()
    return dated[dated["stat_date"] == latest_date].copy()


def _select_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def _sum_column(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return 0.0
    return float(_numeric_series(df, column).sum())


def _case_count(df: pd.DataFrame) -> float:
    if "case_id" in df.columns:
        return float(df["case_id"].nunique())
    return float(len(df))


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def _extract_driver_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _as_list(payload.get("top_drivers"))
    if not rows:
        rows = _as_list(payload.get("attributions"))
    valid_rows = [row for row in rows if isinstance(row, dict)]
    return sorted(valid_rows, key=lambda row: row.get("contribution_rank") or row.get("rank") or 999)


def _first_numeric(item: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = item.get(key)
        if _is_number(value):
            return float(value)
    return None


def _scaled_marker_sizes(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    max_value = float(numeric.max()) if not numeric.empty else 0.0
    if max_value <= 0:
        return [28.0] * len(numeric)
    return (18 + (numeric / max_value) * 52).tolist()


def _ordered_dpd_buckets(values: set[str]) -> list[str]:
    preferred = ["CURRENT", "M0", "M1", "M2", "M3", "M4", "M5", "M6+"]
    ordered = [bucket for bucket in preferred if bucket in values]
    ordered.extend(sorted(bucket for bucket in values if bucket not in preferred))
    return ordered


def _bucket_counts(df: pd.DataFrame, buckets: list[str]) -> list[int]:
    counts = df["dpd_bucket"].astype(str).value_counts()
    return [int(counts.get(bucket, 0)) for bucket in buckets]


def _bucket_rates(counts: list[int]) -> list[float]:
    total = sum(counts)
    if total == 0:
        return [0.0] * len(counts)
    return [count / total for count in counts]
