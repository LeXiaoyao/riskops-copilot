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

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

DASHBOARD_VERSION = "m4-ab-v1"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
TEMPLATE_NAME = "dashboard.html.j2"
_REPO_ROOT = Path(__file__).resolve().parents[3]
_TABLES_YAML = _REPO_ROOT / "metadata" / "tables.yaml"
_METRICS_YAML = _REPO_ROOT / "metadata" / "metric_dictionary.yaml"

# Static portfolio framing — used to make the dashboard self-explanatory
# for visitors without a consumer-finance / collections background.
PROJECT_POSITIONING_EN = (
    "RiskOps Copilot turns post-loan risk operations from scattered SQL / "
    "Excel / PPT work into a reproducible AI / Data workflow: detect "
    "anomaly → explain drivers → generate business report → evaluate "
    "strategy ROI."
)
PROJECT_POSITIONING_CN = (
    "把贷后风控运营里散落在 SQL / Excel / PPT 的工作流，沉淀成可复现的 "
    "AI / Data workflow：识别异常 → 解释驱动 → 生成经营报告 → 估算策略 ROI。"
)

JARGON_GLOSSARY = [
    {
        "term": "M1 D7 recovery rate",
        "plain": "share of newly-overdue (M1) loan amount that gets any payment within day 7",
        "cn": "M1 客户在逾期第 7 天前完成任意还款的金额占比，是贷后早期催收效果的核心指标。",
    },
    {
        "term": "PTP (promise to pay)",
        "plain": "the borrower verbally / textually agrees to pay by a date; PTP keep rate = share that actually paid",
        "cn": "客户口头或文字承诺还款日期；PTP 履约率衡量承诺后真实兑现比例。",
    },
    {
        "term": "Vendor / line",
        "plain": "outsourced collection agency (vendor) and its operation queue (line)",
        "cn": "委外催收机构（vendor）及其作业线路 / 队列（line）。",
    },
    {
        "term": "Recovery rate",
        "plain": "share of overdue principal + interest recovered within a defined window",
        "cn": "在指定窗口内已回收的逾期本息占应收逾期金额的比例。",
    },
    {
        "term": "AI outbound coverage",
        "plain": "share of overdue cases reached by AI-driven outbound calls (demo only — no real customer contact)",
        "cn": "AI 外呼覆盖到的逾期案件占比；本 demo 不产生真实外呼。",
    },
    {
        "term": "Driver / attribution",
        "plain": "which slice (channel / region / customer segment / vendor) explains the change in the headline metric",
        "cn": "解释整体指标变化的关键切片（渠道 / 区域 / 客群 / 供应商等）。",
    },
]

AI_ML_FUSION_LAYERS = [
    {
        "layer": "ML / rules layer",
        "role": "Detect & structure signals",
        "detail_en": "Statistical rules and an offline ML baseline surface anomalies and structure them into typed events with severity.",
        "detail_cn": "统计规则与离线 ML baseline 识别异常，将其结构化为带 severity 的事件。",
    },
    {
        "layer": "Attribution / ROI layer",
        "role": "Quantify business impact",
        "detail_en": "Attribution decomposes the headline drop into ranked drivers; the ROI lab estimates net benefit under demo cost assumptions.",
        "detail_cn": "归因将整体下降拆解为可排序的驱动因素；ROI lab 在 demo 成本假设下估算净收益。",
    },
    {
        "layer": "LLM / Agent layer (planned)",
        "role": "Summarize, explain, draft, route",
        "detail_en": "Later layer will summarize the dashboard, explain drivers in plain language, draft business reports, and route human review.",
        "detail_cn": "后续 layer 负责摘要、口语化解释、报告草稿与人工复核路由。",
    },
    {
        "layer": "Human-in-the-loop boundary",
        "role": "Compliance & approval",
        "detail_en": "LLM is not used as an automatic financial decision maker. Every action requires explicit human approval; no SMS / voice / WhatsApp is sent.",
        "detail_cn": "LLM 不作为自动金融决策者，所有动作必须人工审批；不发送短信 / 语音 / WhatsApp。",
    },
]

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

EVIDENCE_CHAINS = [
    {
        "chain_code": "contact",
        "chain_label": "触达证据",
        "group_codes": ["ai_call"],
        "neutral_phrase": "AI / 人工触达比例",
        "polarity": "negative_when_drop",
    },
    {
        "chain_code": "fulfill",
        "chain_label": "履约证据",
        "group_codes": ["ptp_keep"],
        "neutral_phrase": "PTP 履约",
        "polarity": "negative_when_drop",
    },
    {
        "chain_code": "tool",
        "chain_label": "策略工具证据",
        "group_codes": ["reduction"],
        "neutral_phrase": "减免使用",
        "polarity": "negative_when_drop",
    },
    {
        "chain_code": "compliance",
        "chain_label": "合规证据",
        "group_codes": ["complaint"],
        "neutral_phrase": "投诉率",
        "polarity": "negative_when_rise",
    },
    {
        "chain_code": "capacity",
        "chain_label": "产能压力证据",
        "group_codes": [],
        "neutral_phrase": "人均案量 / 催员负荷",
        "polarity": "negative_when_rise",
    },
]

FIELD_GLOSSARY = [
    {"en": "baseline", "cn": "历史基准", "hint": "基线窗口内的平均水平"},
    {"en": "recent", "cn": "最近窗口", "hint": "最近窗口内的实际表现"},
    {"en": "relative change", "cn": "相对变化", "hint": "最近窗口相对历史基准的变化幅度"},
    {"en": "severity", "cn": "严重度", "hint": "high / medium / low 级，由 M3-A 规则配置决定"},
]

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
    roi_summary: dict[str, Any] | None = None,
    strategy_summary: dict[str, Any] | None = None,
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

    process_groups = _group_process_evidence(process_evidence)
    capacity_signals = _capacity_signals(high_priority)

    driver_displays = [_driver_display(item) for item in top_drivers]
    contribution_max = _max_contribution(driver_displays)
    for driver in driver_displays:
        driver["progress_pct"] = _progress_pct(driver.get("contribution_score"), contribution_max)
        driver["role_explanation"] = _role_explanation(
            driver.get("dimension_name"), driver.get("dimension_value")
        )

    anomaly_displays = [_anomaly_display(item) for item in high_priority]

    evidence_chains = _build_evidence_chains(process_groups, capacity_signals)

    executive_summary = _executive_summary(
        anomaly_count=_safe_int(overview.get("anomaly_count")),
        severity_counts=severity_counts,
        target_anomaly=target_anomaly,
        target_metric_name=target_metric_name,
        target_metric_code=target_metric_code,
        process_groups=process_groups,
        capacity_signals=capacity_signals,
        top_drivers=driver_displays,
    )

    generated_at = generated_at or datetime.now()

    roi_block = _build_roi_block(roi_summary)
    strategy_block = _build_strategy_block(strategy_summary)
    data_layer_table_count = _count_yaml_list(_TABLES_YAML)
    metric_dict_count = _count_yaml_list(_METRICS_YAML)
    portfolio_cards = _build_portfolio_cards(
        anomaly_count=_safe_int(overview.get("anomaly_count")),
        severity_counts=severity_counts,
        target_metric_name=target_metric_name,
        target_metric_code=target_metric_code,
        target_anomaly=target_anomaly,
        top_drivers=driver_displays,
        roi_block=roi_block,
        strategy_block=strategy_block,
        data_layer_table_count=data_layer_table_count,
        metric_dict_count=metric_dict_count,
    )

    return {
        "dashboard_version": DASHBOARD_VERSION,
        "project_title": "RiskOps Copilot",
        "subtitle": "M4 Dashboard & Report MVP",
        "project_positioning_en": PROJECT_POSITIONING_EN,
        "project_positioning_cn": PROJECT_POSITIONING_CN,
        "portfolio_cards": portfolio_cards,
        "ai_ml_fusion_layers": AI_ML_FUSION_LAYERS,
        "jargon_glossary": JARGON_GLOSSARY,
        "data_layer_table_count": data_layer_table_count,
        "metric_dict_count": metric_dict_count,
        "roi_block": roi_block,
        "strategy_block": strategy_block,
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
        "executive_summary": executive_summary,
        "high_priority_anomalies": anomaly_displays,
        "high_priority_glossary": FIELD_GLOSSARY,
        "top_drivers": driver_displays,
        "contribution_max": contribution_max,
        "process_evidence_groups": process_groups,
        "evidence_chains": evidence_chains,
        "capacity_signals": capacity_signals,
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
    env.filters["roi"] = _format_roi
    return env.get_template(TEMPLATE_NAME).render(**context).rstrip() + "\n"


def write_dashboard(input_path: Path, output_path: Path) -> dict[str, Any]:
    summary = load_m3_summary(input_path)
    roi_summary = _load_optional_json(_sibling_outputs(input_path, "model_lab/roi_results.json"))
    strategy_summary = _load_optional_json(
        _sibling_outputs(input_path, "model_lab/strategy_eval_results.json")
    )
    context = build_dashboard_context(
        summary,
        source_path=input_path,
        roi_summary=roi_summary,
        strategy_summary=strategy_summary,
    )
    html = render_dashboard_html(context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return context


def _sibling_outputs(input_path: Path, rel: str) -> Path:
    # M3 summary lives under outputs/m3/m3_summary.json; siblings under outputs/.
    outputs_root = input_path.resolve().parent.parent
    return outputs_root / rel


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _count_yaml_list(path: Path) -> int:
    if not path.exists():
        return 0
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return len(data) if isinstance(data, list) else 0


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


def _max_contribution(drivers: list[dict[str, Any]]) -> float:
    values = [
        d.get("contribution_score")
        for d in drivers
        if isinstance(d.get("contribution_score"), int | float)
    ]
    return max(values) if values else 0.0


def _progress_pct(score: Any, max_score: float) -> float:
    if not isinstance(score, int | float):
        return 0.0
    if max_score <= 0:
        return 0.0
    return max(0.0, min(100.0, (score / max_score) * 100.0))


def _role_explanation(dimension_name: Any, dimension_value: Any) -> str:
    if dimension_name == "channel_code":
        return "电商 / 渠道定位信号，建议下钻产品、供应商、线路。"
    if dimension_name == "province":
        return "地域分群信号，不应直接作为最终策略动作，需结合产能与产品结构。"
    if dimension_name == "score_band":
        if isinstance(dimension_value, str) and dimension_value.upper() in {"A", "B"}:
            return "结构变化信号，检查高质量客群占比或样本结构是否漂移。"
        return "风险分层信号，关注该客群的触达、减免和资源投入。"
    if dimension_name == "risk_level":
        return "风险层信号，结合余额段与入案策略综合判断。"
    if dimension_name == "balance_segment":
        return "余额结构信号，建议联动 risk_level 复核放贷与回收能力。"
    if dimension_name == "vendor_id":
        return "供应商信号，关注线路容量、外呼接通率与合规质检。"
    if dimension_name == "line_id":
        return "线路信号，建议联动产能与外呼策略下钻。"
    return "维度切片信号，需进一步下钻 vendor / line / 产品组合确认。"


def _executive_summary(
    *,
    anomaly_count: int,
    severity_counts: dict[str, Any],
    target_anomaly: dict[str, Any] | None,
    target_metric_name: str,
    target_metric_code: str,
    process_groups: list[dict[str, Any]],
    capacity_signals: list[dict[str, Any]],
    top_drivers: list[dict[str, Any]],
) -> list[str]:
    sentences: list[str] = []
    high = _safe_int(severity_counts.get("high"))
    medium = _safe_int(severity_counts.get("medium"))
    low = _safe_int(severity_counts.get("low"))
    sentences.append(
        f"本期共识别 {anomaly_count} 个异常，其中 {high} 个 high、{medium} 个 medium、{low} 个 low。"
    )

    if target_anomaly:
        rc = target_anomaly.get("relative_change")
        if isinstance(rc, int | float) and rc != 0:
            direction = "下降" if rc < 0 else "上升"
            sentences.append(
                f"核心问题是 {target_metric_name}（{target_metric_code}）{direction}，"
                f"历史基准 {_format_metric_value(target_anomaly.get('baseline_value'))} → "
                f"最近窗口 {_format_metric_value(target_anomaly.get('recent_value'))}，"
                f"相对变化 {_format_signed_pct(rc)}。"
            )
        else:
            sentences.append(
                f"核心问题是 {target_metric_name}（{target_metric_code}）出现异常。"
            )

    accompaniments: list[str] = []
    for group in process_groups:
        deltas = [
            entry.get("delta")
            for entry in group.get("entries", [])
            if isinstance(entry.get("delta"), int | float)
        ]
        if not deltas:
            continue
        avg = sum(deltas) / len(deltas)
        if abs(avg) < 1e-9:
            continue
        if group["group_code"] == "complaint":
            verb = "上升" if avg > 0 else "下降"
        else:
            verb = "下降" if avg < 0 else "上升"
        accompaniments.append(f"{group['group_label']}{verb}")
    for cs in capacity_signals:
        rc = cs.get("relative_change")
        if isinstance(rc, int | float) and rc > 0:
            accompaniments.append("产能压力上升")
            break
    if accompaniments:
        sentences.append("伴随 " + "、".join(accompaniments) + "。")

    if top_drivers:
        pairs = [
            f"{d.get('dimension_name')}={d.get('dimension_value')}"
            for d in top_drivers[:3]
            if d.get("dimension_name") and d.get("dimension_value") is not None
        ]
        if pairs:
            sentences.append("初步归因指向 " + "、".join(pairs) + "。")
        primary = top_drivers[0]
        sentences.append(
            f"建议优先下钻 {primary.get('dimension_name')}={primary.get('dimension_value')}"
            " × vendor / line / score_band，并结合触达和合规证据复核。"
        )

    return sentences


def _build_evidence_chains(
    process_groups: list[dict[str, Any]],
    capacity_signals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_code = {g.get("group_code"): g for g in process_groups}
    chains: list[dict[str, Any]] = []
    for spec in EVIDENCE_CHAINS:
        if spec["chain_code"] == "capacity":
            chains.append(_capacity_chain(spec, capacity_signals))
            continue
        entries: list[dict[str, Any]] = []
        for code in spec["group_codes"]:
            entries.extend(by_code.get(code, {}).get("entries", []))
        chains.append(_process_chain(spec, entries))
    return chains


def _process_chain(spec: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [e.get("delta") for e in entries if isinstance(e.get("delta"), int | float)]
    if not entries or not deltas or all(abs(d) < 1e-9 for d in deltas):
        return {
            "chain_code": spec["chain_code"],
            "chain_label": spec["chain_label"],
            "tone": "neutral",
            "tone_label": "无显著变化",
            "headline": f"本期 {spec['neutral_phrase']} 在 Top drivers 切片中未观察到显著变化。",
            "metric_focus": None,
            "highlight": None,
            "details": entries,
        }
    avg_delta = sum(deltas) / len(deltas)
    if spec["polarity"] == "negative_when_rise":
        tone = "negative" if avg_delta > 0 else "positive"
    else:
        tone = "negative" if avg_delta < 0 else "positive"
    tone_label = "异常恶化" if tone == "negative" else "正向改善"
    highlight = max(
        entries,
        key=lambda e: abs(e.get("delta")) if isinstance(e.get("delta"), int | float) else -1,
    )
    direction = "下降" if (highlight.get("delta") or 0) < 0 else "上升"
    headline = (
        f"{highlight.get('driver')} 的 "
        f"{highlight.get('metric_name_cn') or highlight.get('metric_code')} {direction}："
        f"历史基准 {_format_metric_value(highlight.get('baseline_value'))} → "
        f"最近窗口 {_format_metric_value(highlight.get('recent_value'))}"
        f"（变化 {_format_signed_value(highlight.get('delta'))}）。"
    )
    return {
        "chain_code": spec["chain_code"],
        "chain_label": spec["chain_label"],
        "tone": tone,
        "tone_label": tone_label,
        "headline": headline,
        "metric_focus": highlight.get("metric_name_cn") or highlight.get("metric_code"),
        "highlight": highlight,
        "details": entries,
    }


def _capacity_chain(spec: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, Any]:
    if not signals:
        return {
            "chain_code": spec["chain_code"],
            "chain_label": spec["chain_label"],
            "tone": "neutral",
            "tone_label": "无信号",
            "headline": "本期未捕获产能维度异常。",
            "metric_focus": None,
            "highlight": None,
            "details": [],
        }
    first = signals[0]
    rc = first.get("relative_change")
    if isinstance(rc, int | float):
        tone = "negative" if rc > 0 else "positive"
    else:
        tone = "neutral"
    tone_label = "产能压力上升" if tone == "negative" else "产能压力缓解"
    headline = (
        f"{first.get('metric_name_cn') or first.get('metric_code')}（"
        f"{first.get('dimension_name')}={first.get('dimension_value')}）"
        f"历史基准 {_format_metric_value(first.get('baseline_value'))} → "
        f"最近窗口 {_format_metric_value(first.get('recent_value'))}"
        f"（{_format_signed_pct(rc) if isinstance(rc, int | float) else 'N/A'}）。"
    )
    return {
        "chain_code": spec["chain_code"],
        "chain_label": spec["chain_label"],
        "tone": tone,
        "tone_label": tone_label,
        "headline": headline,
        "metric_focus": first.get("metric_name_cn") or first.get("metric_code"),
        "highlight": first,
        "details": signals,
    }


def _build_portfolio_cards(
    *,
    anomaly_count: int,
    severity_counts: dict[str, Any],
    target_metric_name: str,
    target_metric_code: str,
    target_anomaly: dict[str, Any] | None,
    top_drivers: list[dict[str, Any]],
    roi_block: dict[str, Any] | None,
    strategy_block: dict[str, Any] | None,
    data_layer_table_count: int,
    metric_dict_count: int,
) -> list[dict[str, Any]]:
    high = _safe_int(severity_counts.get("high"))
    medium = _safe_int(severity_counts.get("medium"))
    rc = target_anomaly.get("relative_change") if isinstance(target_anomaly, dict) else None
    if isinstance(rc, int | float) and rc != 0:
        problem_stat = (
            f"{target_metric_name} {_format_signed_pct(rc)} 相对基线"
        )
    else:
        problem_stat = f"{target_metric_name}"
    business_problem = {
        "code": "business_problem",
        "eyebrow": "01 · Business Problem",
        "title": "M1 D7 回收率下降，到底由谁驱动？",
        "stat": problem_stat,
        "description_en": (
            "M1 day-7 recovery rate dropped. Is it driven by channel, "
            "region, customer segment, vendor / line, contact, complaint, "
            "or settlement use? Untangle it without a manual SQL hunt."
        ),
        "description_cn": (
            "M1 D7 回收率下降，需要快速判断到底是渠道、区域、客群、供应商 / "
            "线路、触达、投诉还是减免使用导致，避免靠人工 SQL 反复下钻。"
        ),
    }

    data_metric = {
        "code": "data_metric_layer",
        "eyebrow": "02 · Data & Metric Layer",
        "title": "Synthetic data only · 单一权威源",
        "stat": f"{data_layer_table_count} tables · {metric_dict_count} metrics",
        "description_en": (
            "All numbers come from synthetic data. A 5-layer warehouse, "
            "a metric dictionary (single source of truth) and an enforced "
            "privacy boundary (P0–P4) sit under every panel."
        ),
        "description_cn": (
            "全部基于合成数据；五层数仓 + 指标字典作为单一权威源，"
            "并按 P0–P4 隐私分级约束哪些字段可以进入报告与 LLM 上下文。"
        ),
    }

    anomaly_signal = {
        "code": "anomaly_signals",
        "eyebrow": "03 · Anomaly Signals",
        "title": "结构化异常事件，而非散点告警",
        "stat": f"{anomaly_count} anomalies · {high} high · {medium} medium",
        "description_en": (
            "Rule + ML signals across recovery, AI outbound, manual "
            "capacity, PTP, settlement use and complaint risk are folded "
            "into typed events with severity."
        ),
        "description_cn": (
            "回收率、AI 外呼覆盖、产能压力、PTP、减免使用、投诉风险等信号"
            "统一结构化为带 severity 的事件。"
        ),
    }

    if top_drivers:
        primary = top_drivers[0]
        attr_stat = (
            f"Top driver: {primary.get('dimension_name')}={primary.get('dimension_value')} "
            f"({_format_pct(primary.get('contribution_score'))})"
        )
    else:
        attr_stat = "Top drivers ranked by marginal contribution"
    attribution_card = {
        "code": "attribution",
        "eyebrow": "04 · Attribution",
        "title": "排序好的 Top drivers，可解释",
        "stat": attr_stat,
        "description_en": (
            "Decompose the headline drop into ranked drivers across "
            "channel, region, customer segment and vendor / line, with "
            "process evidence (contact / fulfill / settlement / "
            "compliance / capacity) attached."
        ),
        "description_cn": (
            "把整体下降拆成可排序的驱动因素，并附触达 / 履约 / 减免 / "
            "合规 / 产能五条证据链。"
        ),
    }

    if roi_block and roi_block.get("scenario_count"):
        roi_stat = (
            f"{roi_block['scenario_count']} scenarios · "
            f"top ROI {roi_block.get('top_roi_display', 'N/A')} "
            f"({roi_block.get('top_scenario_name', 'N/A')})"
        )
    else:
        roi_stat = "Demo cost assumptions only"
    strategy_card = {
        "code": "strategy_roi",
        "eyebrow": "05 · Strategy / ROI Lab",
        "title": "离线情景 · 量化净收益与回收周期",
        "stat": roi_stat,
        "description_en": (
            "Offline what-if scenarios estimate delta, cost, net benefit, "
            "ROI and payback days under explicit demo cost assumptions. "
            "Not a production financial decision."
        ),
        "description_cn": (
            "基于显式 demo 成本假设的离线情景估算 delta / cost / net benefit / "
            "ROI / payback，不代表真实财务结论或上线决策。"
        ),
    }

    return [business_problem, data_metric, anomaly_signal, attribution_card, strategy_card]


def _build_roi_block(roi_summary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(roi_summary, dict):
        return None
    results = _as_list(roi_summary.get("results"))
    cost_assumptions = _as_dict(roi_summary.get("cost_assumptions"))
    top = _as_dict(roi_summary.get("highest_roi_scenario"))
    scenarios: list[dict[str, Any]] = []
    for row in results:
        if not isinstance(row, dict):
            continue
        scenarios.append(
            {
                "scenario_id": row.get("scenario_id"),
                "scenario_name": row.get("scenario_name"),
                "strategy_type": row.get("strategy_type"),
                "target_metric": row.get("target_metric"),
                "estimated_delta": row.get("estimated_delta"),
                "estimated_delta_display": _format_signed_value(row.get("estimated_delta")),
                "gross_benefit": row.get("gross_benefit"),
                "action_cost": row.get("action_cost"),
                "net_benefit": row.get("net_benefit"),
                "roi_ratio": row.get("roi_ratio"),
                "roi_ratio_display": _format_roi(row.get("roi_ratio")),
                "payback_period_days": row.get("payback_period_days"),
                "cost_assumption": row.get("cost_assumption"),
            }
        )
    return {
        "scenario_count": _safe_int(roi_summary.get("scenario_count")) or len(scenarios),
        "positive_roi_count": _safe_int(roi_summary.get("positive_roi_count")),
        "top_scenario_id": top.get("scenario_id"),
        "top_scenario_name": top.get("scenario_name"),
        "top_roi_ratio": top.get("roi_ratio"),
        "top_roi_display": _format_roi(top.get("roi_ratio")),
        "cost_assumptions": cost_assumptions,
        "scenarios": scenarios,
        "demo_disclaimer": roi_summary.get("demo_disclaimer"),
    }


def _build_strategy_block(strategy_summary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(strategy_summary, dict):
        return None
    return {
        "scenario_count": _safe_int(strategy_summary.get("scenario_count")),
        "priority_scenarios": _as_list(strategy_summary.get("priority_scenarios")),
        "strategy_type_counts": _as_dict(strategy_summary.get("strategy_type_counts")),
        "target_metric_counts": _as_dict(strategy_summary.get("target_metric_counts")),
        "demo_disclaimer": strategy_summary.get("demo_disclaimer"),
    }


def _format_roi(value: Any) -> str:
    if not isinstance(value, int | float):
        return "N/A"
    return f"{value:.1f}×"
