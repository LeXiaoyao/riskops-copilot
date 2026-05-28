"""Business-facing M4-C report renderer."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

REPORT_VERSION = "m4-c-v1"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
TEMPLATE_NAME = "business_report.md.j2"
DEFAULT_DISCLAIMER = "本报告基于 synthetic_data / 合成数据生成，仅用于 Demo 展示，不代表真实业务结论。"

DRIVER_LABELS = {
    ("channel_code", "ECOM"): {
        "meaning": "ECOM 代表电商渠道来源客群。该分组最近窗口 D7 回收率明显低于基线，说明问题可能集中在渠道客群质量、分案策略或触达资源匹配上。",
        "boundary": "这是切片贡献信号，不等于 ECOM 是唯一根因；channel、province、score_band 之间可能存在样本重叠。",
        "next_step": "优先下钻 ECOM x vendor x line x score_band，确认是否由某个供应商、作业线或客群组合拉低。",
    },
    ("province", "山东"): {
        "meaning": "山东分组回收率下降，提示区域客群、供应商执行或本地作业线排布可能出现同步变化。",
        "boundary": "province 是业务维度切片，不代表单纯地理线路，也不能直接推出区域供应商责任。",
        "next_step": "复核山东区域供应商、line_id、分案批次和 score_band 结构，区分客群结构变化与作业执行变化。",
    },
    ("province", "上海"): {
        "meaning": "上海分组回收率下降，可能与区域客群结构、触达资源切换或供应商执行节奏有关。",
        "boundary": "province 只能说明该切片表现恶化，不能单独证明地理因素导致回收下降。",
        "next_step": "复核上海区域供应商和作业线，重点查看 AI 外呼覆盖、人工触达占比和 PTP 履约表现。",
    },
    ("score_band", "D"): {
        "meaning": "D 分客群通常代表更高风险层。该层回收率下降会直接放大 M1 早期回收压力。",
        "boundary": "score_band 是风险分层信号，不改变 D7 回收率口径，也不代表所有 D 分客群均不可回收。",
        "next_step": "检查 D 分客群触达优先级、催收资源投入、减免授权和 PTP 跟进策略。",
    },
    ("score_band", "A"): {
        "meaning": "A 分客群通常是较优风险层。该层也出现下降，说明问题可能不只发生在高风险客群，需关注流程或资源侧变化。",
        "boundary": "A 分下降不等于模型分层失效；需要结合渠道、区域和作业线进一步验证。",
        "next_step": "检查 A 分客群是否发生渠道结构变化、触达覆盖下降或承诺还款跟进断点。",
    },
}

PROCESS_METRIC_NAMES = {
    "ai_call_coverage": "AI 外呼覆盖",
    "ptp_keep_rate": "PTP 履约",
    "reduction_usage_rate": "减免使用率",
    "complaint_rate": "投诉率",
    "complaint_per_10k_cases": "投诉率",
    "avg_case_per_collector": "人均案量 / 产能压力",
}


class BusinessReportInputError(RuntimeError):
    """Raised when business report input is missing or malformed."""


def load_m3_summary(input_path: Path) -> dict[str, Any]:
    if not input_path.exists():
        raise BusinessReportInputError(
            f"Business report 输入文件不存在：{input_path}。请先生成 outputs/m3/m3_summary.json。"
        )
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BusinessReportInputError(f"Business report 输入文件不是合法 JSON：{input_path}。错误：{exc}") from exc
    if not isinstance(payload, dict):
        raise BusinessReportInputError(f"Business report 输入文件结构不符合预期：{input_path} 顶层必须是 JSON object。")
    return payload


def build_business_report_context(summary: dict[str, Any], *, source_path: Path | None = None) -> dict[str, Any]:
    overview = _as_dict(summary.get("anomaly_overview"))
    severity_counts = _as_dict(overview.get("severity_counts"))
    high_priority = _as_list(summary.get("high_priority_anomalies"))
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))
    target_anomaly = _as_dict(attribution.get("target_anomaly")) or _as_dict(summary.get("attribution_target_anomaly"))
    top_drivers = [_driver_context(item) for item in _as_list(attribution.get("top_drivers"))[:5]]
    process_evidence = _process_evidence_context(_as_list(summary.get("process_evidence")), high_priority)
    capacity_signals = [item for item in high_priority if item.get("metric_code") == "avg_case_per_collector"]
    high_anomalies = [_anomaly_context(item) for item in high_priority]

    severity_summary = [
        {"severity": "high", "count": _safe_int(severity_counts.get("high"))},
        {"severity": "medium", "count": _safe_int(severity_counts.get("medium"))},
        {"severity": "low", "count": _safe_int(severity_counts.get("low"))},
    ]

    return {
        "report_version": REPORT_VERSION,
        "source_path": _path_for_report(source_path) if source_path else None,
        "demo_disclaimer": summary.get("demo_disclaimer") or DEFAULT_DISCLAIMER,
        "overview": {
            "anomaly_count": _safe_int(overview.get("anomaly_count")),
            "severity_counts": severity_counts,
            "severity_summary": severity_summary,
            "baseline_window": overview.get("baseline_window"),
            "recent_window": overview.get("recent_window"),
        },
        "target": _anomaly_context(target_anomaly),
        "target_metric_code": attribution.get("target_metric_code") or "recovery_rate_d7",
        "target_metric_name_cn": attribution.get("target_metric_name_cn") or "D7 回收率",
        "high_priority_anomalies": high_anomalies,
        "top_drivers": top_drivers,
        "process_evidence": process_evidence,
        "capacity_signals": [_anomaly_context(item) for item in capacity_signals],
        "management_actions": [
            "优先下钻 ECOM x vendor x line x score_band，定位是否存在集中异常组合。",
            "复核山东 / 上海区域供应商、催收作业线和分案队列表现。",
            "检查 D 分客群触达策略、资源投入、减免授权和 PTP 跟进是否充分。",
            "检查 AI 外呼覆盖下降原因，确认是容量、策略、名单分配还是人工替代导致。",
            "检查 PTP 履约下降和减免使用不足问题，确认承诺后跟进与策略工具是否断档。",
            "对 TPL_RISK_NOTICE 等投诉风险模板做合规复核，关注发送供应商、时段和话术。",
        ],
        "data_limitations": [
            "本报告使用 synthetic data / 合成数据，不包含真实客户数据。",
            "报告不触发真实催收动作，不包含 SMS / voice automation。",
            "报告不读取、不输出任何 P4 明文字段或字段值。",
            "所有结论用于作品集和面试展示，不代表真实业务结论或真实风控建议。",
            "Top drivers 是切片贡献信号，跨维度可能重叠，不能简单相加为完整根因解释。",
        ],
        "roadmap": [
            "M4 Dashboard polish：继续增强可读性、趋势展示和作品集说明。",
            "M5 TUI：提供命令行交互式工作台，串联异常、归因和报告生成。",
            "M6 Model Lab：建设回收率、PTP 履约、投诉风险等模型实验能力。",
            "M7 Collection QA：扩展催收质检、话术合规检查和策略推荐能力。",
        ],
    }


def render_business_report_markdown(context: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    env.filters["pct"] = _format_pct
    env.filters["metric_value"] = _format_metric_value
    env.filters["signed_metric_value"] = _format_signed_metric_value
    return env.get_template(TEMPLATE_NAME).render(report=context).rstrip() + "\n"


def render_business_report_html(markdown: str, *, title: str = "RiskOps Copilot M4 Business Report") -> str:
    body = _markdown_to_html(markdown)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; background: #f7f8fa; color: #1f2933; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.7; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 40px 24px 64px; background: #ffffff; }}
    h1, h2, h3 {{ color: #111827; line-height: 1.3; }}
    h1 {{ font-size: 32px; margin-bottom: 8px; }}
    h2 {{ margin-top: 36px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 24px; }}
    h3 {{ margin-top: 24px; font-size: 18px; }}
    blockquote {{ margin: 16px 0; padding: 12px 16px; background: #f3f4f6; border-left: 4px solid #64748b; color: #374151; }}
    ul {{ padding-left: 22px; }}
    li {{ margin: 6px 0; }}
    code {{ background: #f3f4f6; padding: 2px 5px; border-radius: 4px; }}
    strong {{ color: #111827; }}
  </style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def write_business_report(
    input_path: Path,
    output_md: Path,
    output_html: Path | None = None,
    output_feishu: Path | None = None,
) -> dict[str, Any]:
    summary = load_m3_summary(input_path)
    context = build_business_report_context(summary, source_path=input_path)
    markdown = render_business_report_markdown(context)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown, encoding="utf-8")
    if output_html is not None:
        output_html.parent.mkdir(parents=True, exist_ok=True)
        output_html.write_text(render_business_report_html(markdown), encoding="utf-8")
    if output_feishu is not None:
        from riskops.engines.report.feishu_md_renderer import render_feishu_markdown

        render_feishu_markdown(summary, output_feishu)
    return context


def _driver_context(driver: dict[str, Any]) -> dict[str, Any]:
    dimension_name = driver.get("dimension_name")
    dimension_value = driver.get("dimension_value")
    label = DRIVER_LABELS.get((dimension_name, dimension_value), {})
    return {
        "rank": driver.get("rank"),
        "dimension_name": dimension_name,
        "dimension_value": dimension_value,
        "baseline_value": driver.get("baseline_value"),
        "recent_value": driver.get("recent_value"),
        "contribution_score": driver.get("contribution_score"),
        "confidence": driver.get("confidence"),
        "business_interpretation": driver.get("business_interpretation"),
        "recommended_action": driver.get("recommended_action"),
        "meaning": label.get("meaning") or f"{dimension_name}={dimension_value} 分组回收表现低于基线，是需要下钻验证的业务切片。",
        "boundary": label.get("boundary") or "该 driver 是统计切片信号，不单独构成最终根因。",
        "next_step": label.get("next_step") or "继续按 vendor、line_id、score_band 和时间窗口下钻验证。",
        "segment_evidence": _as_list(driver.get("segment_evidence")),
        "driver_linkage": _as_list(driver.get("driver_linkage")),
    }


def _anomaly_context(anomaly: dict[str, Any]) -> dict[str, Any]:
    if not anomaly:
        return {}
    return {
        "anomaly_id": anomaly.get("anomaly_id"),
        "metric_code": anomaly.get("metric_code"),
        "metric_name_cn": anomaly.get("metric_name_cn"),
        "severity": anomaly.get("severity"),
        "dimension_name": anomaly.get("dimension_name"),
        "dimension_value": anomaly.get("dimension_value"),
        "baseline_value": anomaly.get("baseline_value"),
        "recent_value": anomaly.get("recent_value"),
        "absolute_change": anomaly.get("absolute_change"),
        "relative_change": anomaly.get("relative_change"),
        "explanation": anomaly.get("explanation"),
        "recommended_next_step": anomaly.get("recommended_next_step"),
        "business_explanation": _business_explanation_for_anomaly(anomaly),
    }


def _business_explanation_for_anomaly(anomaly: dict[str, Any]) -> str:
    metric_code = anomaly.get("metric_code")
    if metric_code == "avg_case_per_collector":
        return "人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。"
    if metric_code == "ai_call_coverage":
        return "AI 外呼覆盖下降说明自动化触达资源或策略发生变化，可能削弱早期提醒和低成本触达能力。"
    if metric_code == "ptp_keep_rate":
        return "PTP 履约下降说明承诺还款后的跟进、客户还款意愿或策略工具支持出现压力。"
    if metric_code == "reduction_usage_rate":
        return "减免使用率下降提示策略工具可能使用不足，需要检查授权、审批、客群准入和供应商执行。"
    if metric_code == "complaint_per_10k_cases":
        return "投诉率升高是合规侧过程风险信号，需要复核模板话术、发送时段和供应商执行。"
    if metric_code == "high_balance_high_risk_share":
        return "高余额高风险客群占比上升会抬高贷后管理难度，可能加剧回收率和产能压力。"
    return "该异常提示经营指标偏离历史基线，需要结合维度、过程证据和作业队列继续下钻。"


def _process_evidence_context(process_rows: list[Any], high_priority: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in process_rows:
        if not isinstance(item, dict):
            continue
        metric_code = item.get("metric_code")
        if metric_code in {"ai_call_coverage", "ptp_keep_rate", "reduction_usage_rate", "complaint_rate"}:
            delta = item.get("delta")
            if isinstance(delta, int | float) and abs(delta) < 0.000001:
                continue
            rows.append(
                {
                    "label": PROCESS_METRIC_NAMES.get(metric_code, str(metric_code)),
                    "metric_code": metric_code,
                    "driver": item.get("driver"),
                    "baseline_value": item.get("baseline_value"),
                    "recent_value": item.get("recent_value"),
                    "delta": delta,
                    "meaning": "process evidence，用于解释过程链路变化，不能单独视为最终根因。",
                }
            )
    for item in high_priority:
        if not isinstance(item, dict):
            continue
        metric_code = item.get("metric_code")
        if metric_code in {"ai_call_coverage", "ptp_keep_rate", "reduction_usage_rate", "complaint_per_10k_cases", "avg_case_per_collector"}:
            rows.append(
                {
                    "label": PROCESS_METRIC_NAMES.get(metric_code, item.get("metric_name_cn")),
                    "metric_code": metric_code,
                    "driver": f"{item.get('dimension_name')}={item.get('dimension_value')}",
                    "baseline_value": item.get("baseline_value"),
                    "recent_value": item.get("recent_value"),
                    "delta": item.get("absolute_change"),
                    "meaning": _business_explanation_for_anomaly(item),
                }
            )
    return _dedupe_evidence(rows)


def _dedupe_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, Any, Any]] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        key = (row.get("metric_code"), row.get("driver"), row.get("recent_value"))
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def _markdown_to_html(markdown: str) -> str:
    lines: list[str] = []
    in_list = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line:
            if in_list:
                lines.append("</ul>")
                in_list = False
            continue
        if line.startswith("### "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h3>{_inline_markdown(line[4:])}</h3>")
        elif line.startswith("## "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h2>{_inline_markdown(line[3:])}</h2>")
        elif line.startswith("# "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<h1>{_inline_markdown(line[2:])}</h1>")
        elif line.startswith("> "):
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<blockquote>{_inline_markdown(line[2:])}</blockquote>")
        elif line.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            lines.append(f"<li>{_inline_markdown(line[2:])}</li>")
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<p>{_inline_markdown(line)}</p>")
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


def _inline_markdown(value: str) -> str:
    escaped = html.escape(value)
    parts = escaped.split("**")
    if len(parts) == 1:
        return escaped
    rendered: list[str] = []
    strong = False
    for part in parts:
        if strong:
            rendered.append(f"<strong>{part}</strong>")
        else:
            rendered.append(part)
        strong = not strong
    return "".join(rendered)


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


def _path_for_report(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _format_pct(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.2%}"
    return "N/A"


def _format_metric_value(value: Any) -> str:
    if not isinstance(value, int | float):
        return "N/A"
    if abs(value) <= 1:
        return f"{value:.2%}"
    return f"{value:,.2f}"


def _format_signed_metric_value(value: Any) -> str:
    if not isinstance(value, int | float):
        return "N/A"
    if abs(value) <= 1:
        return f"{value:+.2%}"
    return f"{value:+,.2f}"
