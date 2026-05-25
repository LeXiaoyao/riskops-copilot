"""Deterministic Copilot briefing builder.

Aggregates M3 / strategy_eval / ROI / ML outputs into a structured
management briefing. Rule-based template composition — does not call LLM.
Belongs to M7 demo packaging, not M5/M8 LLM Agent layer.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_copilot_briefing(
    m3_summary_path: str | Path,
    strategy_eval_path: str | Path,
    roi_path: str | Path,
    ml_metrics_path: str | Path,
    ml_readiness_path: str | Path,
) -> dict[str, Any]:
    m3_summary = _load_json_object(m3_summary_path)
    strategy_eval = _load_json_object(strategy_eval_path)
    roi = _load_json_object(roi_path)
    ml_metrics = _load_json_object(ml_metrics_path)
    ml_readiness = _load_json_object(ml_readiness_path)

    overview = _as_dict(m3_summary.get("anomaly_overview"))
    attribution = _as_dict(m3_summary.get("m1_d7_attribution_summary"))
    target = _as_dict(attribution.get("target_anomaly")) or _as_dict(m3_summary.get("attribution_target_anomaly"))
    drivers = [_as_dict(item) for item in _as_list(attribution.get("top_drivers"))[:5]]
    anomalies = [_as_dict(item) for item in _as_list(m3_summary.get("high_priority_anomalies"))[:5]]
    strategy_results = [_as_dict(item) for item in _as_list(strategy_eval.get("results"))]
    roi_results = [_as_dict(item) for item in _as_list(roi.get("results"))]

    top_strategy = _top_strategy(strategy_results, roi)
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "briefing_type": "deterministic_rule_based",
        "what_happened": {
            "anomaly_count": _safe_int(overview.get("anomaly_count")),
            "severity_counts": _as_dict(overview.get("severity_counts")),
            "baseline_window": overview.get("baseline_window"),
            "recent_window": overview.get("recent_window"),
            "target_metric": target.get("metric_code") or attribution.get("target_metric_code") or "recovery_rate_d7",
            "target_metric_name": target.get("metric_name_cn") or attribution.get("target_metric_name_cn") or "D7 回收率",
            "target_relative_change": target.get("relative_change"),
            "top_anomalies": anomalies,
        },
        "why": {
            "top_drivers": drivers,
            "process_note": "drivers are attribution signals, not final root cause",
        },
        "strategy_lab": {
            "priority_scenarios": _as_list(strategy_eval.get("priority_scenarios")),
            "top_strategy": top_strategy,
            "positive_roi_count": _safe_int(roi.get("positive_roi_count")),
        },
        "ml_baseline": {
            "recommended_target": ml_readiness.get("recommended_target"),
            "best_model": ml_metrics.get("best_model"),
            "row_count": _safe_int(ml_metrics.get("row_count")),
            "positive_rate": ml_metrics.get("positive_rate"),
            "auc": ml_metrics.get("auc"),
            "ks": ml_metrics.get("ks"),
            "top_decile_capture_rate": ml_metrics.get("top_decile_capture_rate"),
            "top_features": _as_list(ml_metrics.get("top_feature_importance"))[:5],
            "caveats": _as_list(ml_metrics.get("caveats")),
        },
        "what_to_check": _what_to_check(drivers, top_strategy),
        "what_not_to_conclude": [
            "Do not treat this as a production model or real financial forecast.",
            "Do not treat attribution drivers as final root cause without operational validation.",
            "Do not use this briefing for automated collection action, SMS, voice, WhatsApp, or customer-level decisioning.",
            "Do not send PII or real customer data into LLM context.",
        ],
        "next_actions": _next_actions(top_strategy),
        "boundary": [
            "synthetic data only",
            "rule-based deterministic briefing",
            "no LLM automatic decisioning",
            "no real customer data",
            "no real collection action",
        ],
    }


def render_copilot_briefing(briefing: dict[str, Any]) -> str:
    happened = briefing["what_happened"]
    why = briefing["why"]
    strategy = briefing["strategy_lab"]
    ml = briefing["ml_baseline"]
    lines = [
        "# RiskOps Copilot Briefing",
        "",
        "## Boundary",
        "",
        "- This briefing is deterministic and rule-based.",
        "- It does not call an LLM.",
        "- It must not be used for automatic financial or collection decisioning.",
        "- Inputs are synthetic demo outputs only.",
        "",
        "## What Happened",
        "",
        f"- **anomaly_count**：{happened['anomaly_count']}",
        f"- **severity_counts**：high={_safe_int(happened['severity_counts'].get('high'))}, medium={_safe_int(happened['severity_counts'].get('medium'))}, low={_safe_int(happened['severity_counts'].get('low'))}",
        f"- **window**：baseline={happened['baseline_window']}, recent={happened['recent_window']}",
        f"- **target_metric**：{happened['target_metric_name']}（{happened['target_metric']}）",
        f"- **target_relative_change**：{_format_pct(happened.get('target_relative_change'), signed=True)}",
        "",
        "## Why It May Be Happening",
        "",
        "- Top drivers are directional attribution signals, not final root cause.",
    ]
    for driver in why["top_drivers"]:
        lines.append(
            f"- **{driver.get('dimension_name')}={driver.get('dimension_value')}**：contribution={_format_pct(driver.get('contribution_score'))}; action={driver.get('recommended_action')}"
        )
    top_strategy = strategy["top_strategy"]
    lines.extend(
        [
            "",
            "## What To Check",
            "",
        ]
    )
    for item in briefing["what_to_check"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Strategy Lab Signal",
            "",
            f"- **priority_scenarios**：{', '.join(str(item) for item in strategy['priority_scenarios']) or 'none'}",
            f"- **top_strategy**：{top_strategy.get('scenario_id', 'none')}",
            f"- **estimated_delta**：{_format_pct(top_strategy.get('estimated_delta'))}",
            f"- **roi_ratio**：{_format_number(top_strategy.get('roi_ratio'))}",
            f"- **positive_roi_count**：{strategy['positive_roi_count']}",
            "",
            "## ML Baseline Signal",
            "",
            f"- **recommended_target**：{ml['recommended_target']}",
            f"- **best_model**：{ml['best_model']}",
            f"- **row_count**：{ml['row_count']}",
            f"- **positive_rate**：{_format_pct(ml.get('positive_rate'))}",
            f"- **AUC**：{_format_number(ml.get('auc'))}",
            f"- **KS**：{_format_number(ml.get('ks'))}",
            f"- **top_decile_capture_rate**：{_format_pct(ml.get('top_decile_capture_rate'))}",
            "",
            "## What Not To Conclude",
            "",
        ]
    )
    for item in briefing["what_not_to_conclude"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Actions", ""])
    for item in briefing["next_actions"]:
        lines.append(f"- {item}")
    lines.extend(["", f"_Generated at {briefing['generated_at']}_", ""])
    return "\n".join(lines)


def write_copilot_briefing(briefing: dict[str, Any], output_path: str | Path) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_copilot_briefing(briefing), encoding="utf-8")
    return str(path)


def render_copilot_briefing_with_narrative(
    briefing: dict[str, Any],
    narrative: str,
) -> str:
    """Prepend LLM narrative section to the deterministic briefing."""
    deterministic = render_copilot_briefing(briefing)
    header = "\n".join([
        "# RiskOps Copilot Briefing（AI 增强版）",
        "",
        "> **AI 摘要** 由 DeepSeek LLM 生成，仅供参考。",
        "> 以下结构化数据段（What Happened 等）为确定性规则输出，是唯一可追溯的权威信源。",
        "",
        "## AI 管理层摘要",
        "",
        narrative.strip(),
        "",
        "---",
        "",
    ])
    # 替换掉 deterministic 里的第一行标题，避免重复
    deterministic_body = "\n".join(deterministic.split("\n")[1:]).lstrip("\n")
    return header + deterministic_body


def write_copilot_briefing_with_narrative(
    briefing: dict[str, Any],
    narrative: str,
    output_path: str | Path,
) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_copilot_briefing_with_narrative(briefing, narrative),
        encoding="utf-8",
    )
    return str(path)


def _top_strategy(strategy_results: list[dict[str, Any]], roi: dict[str, Any]) -> dict[str, Any]:
    highest = _as_dict(roi.get("highest_roi_scenario"))
    scenario_id = highest.get("scenario_id")
    strategy = next((item for item in strategy_results if item.get("scenario_id") == scenario_id), {})
    return {
        "scenario_id": scenario_id or strategy.get("scenario_id") or "none",
        "scenario_name": highest.get("scenario_name") or strategy.get("scenario_name"),
        "estimated_delta": strategy.get("estimated_delta"),
        "roi_ratio": highest.get("roi_ratio"),
        "recommended_action": strategy.get("recommended_action"),
    }


def _what_to_check(drivers: list[dict[str, Any]], top_strategy: dict[str, Any]) -> list[str]:
    checks = [
        "Validate whether top attribution segments remain abnormal at vendor, line, and customer segment cuts.",
        "Check process evidence around AI coverage, manual capacity, connect rate, PTP, complaints, and reduction usage before action.",
    ]
    if top_strategy.get("scenario_id") and top_strategy.get("scenario_id") != "none":
        checks.append(f"Review offline assumptions behind scenario `{top_strategy['scenario_id']}` before treating ROI as directional.")
    if drivers:
        first = drivers[0]
        checks.append(f"Start drilldown from `{first.get('dimension_name')}={first.get('dimension_value')}` because it has the highest contribution score.")
    return checks


def _next_actions(top_strategy: dict[str, Any]) -> list[str]:
    actions = [
        "Run segment-level validation on the top drivers and confirm whether the signal is stable across recent days.",
        "Use model baseline only as a ranking diagnostics demo; keep production-model claims out of the narrative.",
        "Document any unresolved metric or timing ambiguity before expanding ML targets.",
    ]
    if top_strategy.get("recommended_action"):
        actions.insert(0, str(top_strategy["recommended_action"]))
    return actions


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _format_pct(value: Any, *, signed: bool = False) -> str:
    if not isinstance(value, int | float):
        return "-"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value * 100:.2f}%"


def _format_number(value: Any) -> str:
    if not isinstance(value, int | float):
        return "-"
    return f"{value:.2f}"


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
