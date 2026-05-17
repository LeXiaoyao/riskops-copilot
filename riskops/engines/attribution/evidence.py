"""Evidence builders for attribution output."""

from __future__ import annotations

import pandas as pd

from riskops.engines.attribution.decomposition import WindowSpec, safe_rate


PROCESS_METRICS = {
    "connect_rate": ("connected_count", "action_count", "接通率"),
    "ai_call_coverage": ("ai_action_count", "action_count", "AI 外呼覆盖率"),
    "manual_call_coverage": ("manual_action_count", "action_count", "人工触达占比"),
    "ptp_keep_rate": ("ptp_fulfilled_count", "ptp_count", "PTP 履约率"),
    "reduction_usage_rate": ("reduction_used", "loan_id", "减免使用率"),
    "complaint_rate": ("complaint_flag", "loan_id", "投诉率"),
}


def process_metric_snapshot(fact: pd.DataFrame, dimension: str, value: str, window: WindowSpec) -> list[dict[str, object]]:
    subset = fact[fact[dimension].astype(str).eq(str(value))].copy()
    if subset.empty:
        return []
    rows: list[dict[str, object]] = []
    for metric_code, (num_col, den_col, name_cn) in PROCESS_METRICS.items():
        if num_col not in subset.columns or den_col not in subset.columns:
            continue
        baseline = subset[(subset["stat_date"] >= window.baseline_start) & (subset["stat_date"] <= window.baseline_end)]
        recent = subset[(subset["stat_date"] >= window.recent_start) & (subset["stat_date"] <= window.recent_end)]
        if baseline.empty or recent.empty:
            continue
        if den_col == "loan_id":
            baseline_den = float(baseline[den_col].nunique())
            recent_den = float(recent[den_col].nunique())
            baseline_num = float(baseline[num_col].sum())
            recent_num = float(recent[num_col].sum())
        else:
            baseline_num = float(pd.to_numeric(baseline[num_col], errors="coerce").fillna(0).sum())
            baseline_den = float(pd.to_numeric(baseline[den_col], errors="coerce").fillna(0).sum())
            recent_num = float(pd.to_numeric(recent[num_col], errors="coerce").fillna(0).sum())
            recent_den = float(pd.to_numeric(recent[den_col], errors="coerce").fillna(0).sum())
        baseline_value = safe_rate(baseline_num, baseline_den)
        recent_value = safe_rate(recent_num, recent_den)
        rows.append(
            {
                "metric_code": metric_code,
                "metric_name_cn": name_cn,
                "baseline_value": round(baseline_value, 6),
                "recent_value": round(recent_value, 6),
                "delta": round(recent_value - baseline_value, 6),
            }
        )
    return rows


def build_evidence(row: pd.Series, process_metrics: list[dict[str, object]]) -> list[dict[str, object]]:
    evidence = [
        {
            "method": "segment_delta",
            "baseline_value": round(float(row["value_baseline"]), 6),
            "recent_value": round(float(row["value_recent"]), 6),
            "delta": round(float(row["delta"]), 6),
            "baseline_loan_count": int(row.get("loan_count_baseline", 0)),
            "recent_loan_count": int(row.get("loan_count_recent", 0)),
            "baseline_denominator": round(float(row["denominator_baseline"]), 2),
            "recent_denominator": round(float(row["denominator_recent"]), 2),
            "recent_weight": round(float(row.get("recent_weight", 0)), 6),
        }
    ]
    for metric in process_metrics:
        evidence.append({"method": "driver_linkage", **metric})
    return evidence


def interpretation_for(dimension: str, value: str, process_metrics: list[dict[str, object]]) -> tuple[str, str, str]:
    negative_metrics = [item for item in process_metrics if float(item.get("delta", 0)) < 0]
    positive_risk = [item for item in process_metrics if item.get("metric_code") == "complaint_rate" and float(item.get("delta", 0)) > 0]
    if dimension in {"vendor_id", "vendor_name"}:
        return (
            f"{value} 的 M1 D7 回收率降幅对整体下降贡献较高，需优先核查供应商执行质量。",
            "复盘该供应商近 30 天接通、PTP 履约和减免使用，必要时调整分案或补充产能。",
            "high" if negative_metrics or positive_risk else "medium",
        )
    if dimension in {"line_id", "line_name", "region"}:
        return (
            f"{value} 对回收率下降贡献较高，可能与线路资源、区域案源结构或产能压力有关。",
            "按线路核查人均案量、在催案件和催员可用产能，优先处理高贡献线路。",
            "high" if negative_metrics or positive_risk else "medium",
        )
    if dimension in {"risk_level", "balance_segment", "score_band", "dpd_bucket"}:
        return (
            f"{value} 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。",
            "对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。",
            "medium",
        )
    if dimension in {"ai_call_coverage", "manual_call_coverage", "ptp_keep_rate", "reduction_usage_rate", "complaint_rate"}:
        return (
            f"{value} 对应的过程执行状态与回收率下降同步出现，支持过程指标作为解释链路。",
            "定位对应案件集合，检查触达策略、承诺还款跟进、减免授权或投诉管控是否发生变化。",
            "medium",
        )
    return (
        f"{value} 分组的回收率下降对整体异常有可量化贡献。",
        "继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。",
        "medium",
    )
