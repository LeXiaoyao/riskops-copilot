"""Static HTML dashboard builder for M4-A/B MVP.

Consumes the M3 structured summary JSON and renders a self-contained
HTML dashboard for portfolio / demo display. Does not modify M3 outputs
and does not redefine any metric values — formatting only happens in
the presentation layer.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

DASHBOARD_VERSION = "m4-ab-v1"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
TEMPLATE_NAME = "dashboard.html.j2"

PROCESS_METRIC_GROUPS = [
    {
        "group_code": "ptp_keep",
        "group_label": "PTP 履约",
        "metric_codes": ["ptp_keep_rate"],
    },
    {
        "group_code": "ai_call",
        "group_label": "AI 外呼覆盖",
        "metric_codes": ["ai_call_coverage", "manual_call_coverage"],
    },
    {
        "group_code": "reduction",
        "group_label": "减免使用率",
        "metric_codes": ["reduction_usage_rate"],
    },
    {
        "group_code": "complaint",
        "group_label": "投诉率",
        "metric_codes": ["complaint_rate"],
    },
]

CAPACITY_METRIC_CODES = {"avg_case_per_collector"}

NEXT_PHASE_ROADMAP = [
    {
        "phase": "M4 后续增强",
        "bullets": [
            "经营报告 renderer（Word / PPT）输出客户经营分析报告",
            "Dashboard 增加趋势图、下钻 link、对比窗口切换",
        ],
    },
    {
        "phase": "M5 TUI",
        "bullets": [
            "Textual TUI 工作台：异常 / 归因 / 报告一键运行",
            "命令行交互式选择目标指标 / 维度 / 时间窗口",
        ],
    },
    {
        "phase": "M6 Model Lab",
        "bullets": [
            "回收率模型、PTP 履约模型、投诉风险模型实验台",
            "AUC / KS / PSI / lift 评估报告与基线对比",
        ],
    },
    {
        "phase": "M7 Collection QA",
        "bullets": [
            "催收录音 / 文本质检与合规风险识别",
            "话术推荐与 AI 外呼场景化策略",
        ],
    },
]


class DashboardInputError(RuntimeError):
    """Raised when dashboard input JSON is missing or malformed."""


def load_m3_summary(input_path: Path) -> dict[str, Any]:
    if not input_path.exists():
        raise DashboardInputError(
            f"Dashboard 输入文件不存在：{input_path}。"
            "请先运行 scripts/detect_anomalies.py、scripts/run_attribution.py 和 scripts/render_m3_report.py 生成 m3_summary.json。"
        )
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DashboardInputError(
            f"Dashboard 输入文件不是合法 JSON：{input_path}。错误：{exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise DashboardInputError(
            f"Dashboard 输入文件结构不符合预期：{input_path} 顶层必须是 JSON object。"
        )
    return payload


def build_dashboard_context(
    summary: dict[str, Any],
    *,
    source_path: Path | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Enrich the raw M3 summary into a template-ready context.

    Original numeric values are kept as-is on the summary; we only
    attach pre-formatted display strings for HTML rendering.
    """
    overview = _as_dict(summary.get("anomaly_overview"))
    severity_counts = _as_dict(overview.get("severity_counts"))
    attribution_summary = _as_dict(summary.get("m1_d7_attribution_summary"))
    top_drivers = _as_list(attribution_summary.get("top_drivers"))
    high_priority = _as_list(summary.get("high_priority_anomalies"))
    process_evidence = _as_list(summary.get("process_evidence"))
    data_limitations = _as_list(summary.get("data_limitations"))
    next_steps = _as_list(summary.get("next_steps"))

    target_anomaly = (
        _as_dict(attribution_summary.get("target_anomaly"))
        or _as_dict(summary.get("attribution_target_anomaly"))
    )
    target_metric_name = (
        attribution_summary.get("target_metric_name_cn")
        or target_anomaly.get("metric_name_cn")
        or "D7 回收率"
    )
    target_metric_code = attribution_summary.get("target_metric_code") or "recovery_rate_d7"

    overview_cards = [
        {"label": "异常总数", "value": _safe_int(overview.get("anomaly_count")), "tone": "neutral"},
        {"label": "high 级", "value": _safe_int(severity_counts.get("high")), "tone": "high"},
        {"label": "medium 级", "value": _safe_int(severity_counts.get("medium")), "tone": "medium"},
        {"label": "low 级", "value": _safe_int(severity_counts.get("low")), "tone": "low"},
    ]

    generated_at = generated_at or datetime.now()

    return {
        "dashboard_version": DASHBOARD_VERSION,
        "project_title": "RiskOps Copilot",
        "subtitle": "M4 Dashboard & Report MVP",
        "demo_disclaimer": summary.get("demo_disclaimer")
        or "本报告基于 synthetic_data / 合成数据生成，仅用于 Demo 展示，不代表真实业务结论。",
        "report_version": summary.get("report_version"),
        "source_files": _as_dict(summary.get("source_files")),
        "input_source_path": str(source_path) if source_path else None,
        "generated_at_display": generated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "overview": {
            "anomaly_count": _safe_int(overview.get("anomaly_count")),
            "severity_counts": severity_counts,
            "baseline_window": overview.get("baseline_window"),
            "recent_window": overview.get("recent_window"),
            "warnings": _as_list(overview.get("warnings")),
            "cards": overview_cards,
        },
        "attribution_target": {
            "metric_name_cn": target_metric_name,
            "metric_code": target_metric_code,
            "anomaly_id": attribution_summary.get("target_anomaly_id"),
            "anomaly": _anomaly_display(target_anomaly) if target_anomaly else None,
        },
        "high_priority_anomalies": [_anomaly_display(item) for item in high_priority],
        "top_drivers": [_driver_display(item) for item in top_drivers],
        "process_evidence_groups": _group_process_evidence(process_evidence),
        "capacity_signals": _capacity_signals(high_priority),
        "data_limitations": data_limitations,
        "next_steps": next_steps,
        "roadmap": NEXT_PHASE_ROADMAP,
    }


def render_dashboard_html(context: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "htm", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    env.filters["pct"] = _format_pct
    env.filters["signed_pct"] = _format_signed_pct
    env.filters["metric_value"] = _format_metric_value
    env.filters["signed_value"] = _format_signed_value
    return env.get_template(TEMPLATE_NAME).render(**context).rstrip() + "\n"


def write_dashboard(input_path: Path, output_path: Path) -> dict[str, Any]:
    summary = load_m3_summary(input_path)
    context = build_dashboard_context(summary, source_path=input_path)
    html = render_dashboard_html(context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return context


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return int(value)
    return 0


def _anomaly_display(anomaly: dict[str, Any]) -> dict[str, Any]:
    return {
        "anomaly_id": anomaly.get("anomaly_id"),
        "metric_code": anomaly.get("metric_code"),
        "metric_name_cn": anomaly.get("metric_name_cn"),
        "severity": anomaly.get("severity"),
        "anomaly_type": anomaly.get("anomaly_type"),
        "dimension_name": anomaly.get("dimension_name"),
        "dimension_value": anomaly.get("dimension_value"),
        "baseline_value": anomaly.get("baseline_value"),
        "recent_value": anomaly.get("recent_value"),
        "absolute_change": anomaly.get("absolute_change"),
        "relative_change": anomaly.get("relative_change"),
        "baseline_window": anomaly.get("baseline_window"),
        "recent_window": anomaly.get("recent_window"),
        "evidence_table": anomaly.get("evidence_table"),
        "explanation": anomaly.get("explanation"),
        "recommended_next_step": anomaly.get("recommended_next_step"),
    }


def _driver_display(driver: dict[str, Any]) -> dict[str, Any]:
    return {
        "attribution_id": driver.get("attribution_id"),
        "rank": driver.get("rank"),
        "dimension_name": driver.get("dimension_name"),
        "dimension_value": driver.get("dimension_value"),
        "baseline_value": driver.get("baseline_value"),
        "recent_value": driver.get("recent_value"),
        "contribution_score": driver.get("contribution_score"),
        "business_interpretation": driver.get("business_interpretation"),
        "recommended_action": driver.get("recommended_action"),
        "confidence": driver.get("confidence"),
        "driver_role": _driver_role(driver.get("dimension_name")),
    }


def _driver_role(dimension_name: Any) -> str:
    role_map = {
        "channel_code": "渠道结构",
        "province": "区域结构",
        "score_band": "客群风险结构",
        "risk_level": "客群风险结构",
        "balance_segment": "余额结构",
        "vendor_id": "供应商",
        "line_id": "线路",
        "dpd_bucket": "逾期阶段",
    }
    if isinstance(dimension_name, str) and dimension_name in role_map:
        return role_map[dimension_name]
    return "维度切片"


def _group_process_evidence(rows: list[Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for spec in PROCESS_METRIC_GROUPS:
        entries: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            if row.get("metric_code") in spec["metric_codes"]:
                entries.append(
                    {
                        "driver": row.get("driver"),
                        "metric_code": row.get("metric_code"),
                        "metric_name_cn": row.get("metric_name_cn"),
                        "baseline_value": row.get("baseline_value"),
                        "recent_value": row.get("recent_value"),
                        "delta": row.get("delta"),
                    }
                )
        groups.append(
            {
                "group_code": spec["group_code"],
                "group_label": spec["group_label"],
                "entries": entries,
            }
        )
    return groups


def _capacity_signals(high_priority: list[Any]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for item in high_priority:
        if not isinstance(item, dict):
            continue
        if item.get("metric_code") in CAPACITY_METRIC_CODES:
            signals.append(_anomaly_display(item))
    return signals


def _format_pct(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.2%}"
    return "N/A"


def _format_signed_pct(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:+.2%}"
    return "N/A"


def _format_metric_value(value: Any) -> str:
    if not isinstance(value, int | float):
        return "N/A"
    if abs(value) <= 1:
        return f"{value:.2%}"
    return f"{value:,.2f}"


def _format_signed_value(value: Any) -> str:
    if not isinstance(value, int | float):
        return "N/A"
    if abs(value) <= 1:
        return f"{value:+.2%}"
    return f"{value:+,.2f}"
