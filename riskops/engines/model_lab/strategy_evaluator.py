"""Offline M6-B strategy evaluator for demo scenarios."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from riskops.engines.model_lab.scenario_schema import load_strategy_scenarios, validate_strategy_scenarios

REPORT_VERSION = "m6-b-v1"
DEFAULT_DISCLAIMER = (
    "本报告基于 synthetic data / 合成数据和 M3 规则输出生成，仅用于离线 demo estimate，"
    "不代表真实业务结论、真实策略引擎或真实财务结果。"
)
BUSINESS_BOUNDARIES = [
    "不是真实策略引擎。",
    "不自动决策。",
    "不产生真实催收动作。",
    "不发送 SMS / voice / WhatsApp。",
    "不调用 LLM 做策略决策。",
    "不代表真实财务结果。",
    "不改变 M1/M2/M3 指标口径。",
]
SCENARIO_RULES = {
    "increase_ai_call_coverage": {
        "delta": 0.006,
        "direction": "improve",
        "confidence": "medium",
        "keyword": "ai_call_coverage",
        "recommended_action": "优先复核 AI 外呼覆盖下降的渠道和区域切片，离线评估恢复覆盖后的 D7 回收率改善空间。",
        "caveat": "这是触达补强假设，不代表真实外呼动作，也不证明覆盖提升一定带来回收提升。",
    },
    "increase_manual_capacity": {
        "delta": 0.004,
        "direction": "reduce_risk",
        "confidence": "medium",
        "keyword": "avg_case_per_collector",
        "recommended_action": "优先评估华东作业线临时增员或分案转移的影响面，观察产能压力缓解方向。",
        "caveat": "人均案量是 capacity pressure signal，不是最终根因；仍需结合客群结构和触达质量验证。",
    },
    "adjust_reduction_usage": {
        "delta": 0.003,
        "direction": "improve",
        "confidence": "low",
        "keyword": "reduction_usage_rate",
        "recommended_action": "复核减免授权、审批门槛和适用客群，离线观察适度提高减免使用后的回收改善方向。",
        "caveat": "该估算不代表真实减免审批，也不计算 ROI；成本收益留给 M6-C 单独处理。",
    },
    "vendor_reallocation": {
        "delta": 0.005,
        "direction": "reduce_risk",
        "confidence": "medium",
        "keyword": "region",
        "recommended_action": "围绕 ECOM、山东、上海、华东和作业线组合做资源再分配模拟，避免直接写成供应商责任结论。",
        "caveat": "line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路；资源再分配只是离线估算。",
    },
    "score_band_D_priority": {
        "delta": 0.002,
        "direction": "monitor",
        "confidence": "medium",
        "keyword": "score_band=D",
        "recommended_action": "将 score_band=D 作为优先跟进分层线索，离线观察触达、PTP 和减免跟进策略的影响面。",
        "caveat": "score_band 是分层线索，不是最终根因；不生成真实客户名单，不训练或调用评分模型。",
    },
}


def load_m3_summary(path: str | Path) -> dict[str, Any]:
    summary_path = Path(path)
    if not summary_path.exists():
        raise FileNotFoundError(f"M3 summary not found: {summary_path}")
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"M3 summary is invalid JSON: {summary_path}. Error: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"M3 summary must be a JSON object: {summary_path}")
    return payload


def evaluate_strategy_scenarios(scenarios: list[dict[str, Any]], m3_summary: dict[str, Any]) -> dict[str, Any]:
    errors = validate_strategy_scenarios(scenarios)
    if errors:
        raise ValueError(f"Invalid strategy scenarios: {errors}")

    results = [_evaluate_one(scenario, m3_summary) for scenario in scenarios]
    strategy_type_counts = Counter(result["strategy_type"] for result in results)
    target_metric_counts = Counter(result["target_metric"] for result in results)
    priority_scenarios = [
        result["scenario_id"]
        for result in results
        if result["estimated_direction"] in {"improve", "reduce_risk"} and result["confidence"] in {"medium", "high"}
    ]
    return {
        "report_version": REPORT_VERSION,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "demo_disclaimer": DEFAULT_DISCLAIMER,
        "scenario_count": len(results),
        "strategy_type_counts": dict(sorted(strategy_type_counts.items())),
        "target_metric_counts": dict(sorted(target_metric_counts.items())),
        "priority_scenarios": priority_scenarios,
        "results": results,
        "business_boundary": BUSINESS_BOUNDARIES,
    }


def run_strategy_evaluation(
    scenarios_path: str | Path,
    m3_summary_path: str | Path,
    output_json: str | Path,
    output_md: str | Path,
) -> dict[str, Any]:
    scenarios = load_strategy_scenarios(scenarios_path)
    summary = load_m3_summary(m3_summary_path)
    report = evaluate_strategy_scenarios(scenarios, summary)
    write_strategy_eval_results(report, output_json)
    write_strategy_eval_summary(report, output_md)
    return report


def write_strategy_eval_results(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_strategy_eval_summary(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_strategy_eval_markdown(report), encoding="utf-8")


def render_strategy_eval_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# M6-B Offline Strategy Evaluation Summary",
        "",
        "## 1. Demo Disclaimer",
        "",
        f"- {report['demo_disclaimer']}",
        "- synthetic data only",
        "- no real customer data",
        "- no real collection action",
        "- no SMS / voice / WhatsApp",
        "- no LLM decisioning",
        "",
        "## 2. Executive Summary",
        "",
        f"- **scenario count**：{report['scenario_count']}",
        f"- **target metric**：{', '.join(report['target_metric_counts'].keys())}",
        f"- **priority scenarios**：{', '.join(report['priority_scenarios']) or 'none'}",
        "- **判断边界**：所有结果都是 offline demo estimate，不是真实预测。",
        "- **优先方向**：先看 AI 外呼覆盖补强、人工产能缓解和资源再分配；减免策略和 D 分客群优先级需要继续观察假设。",
        "",
        "## 3. Scenario Results",
        "",
    ]
    for result in report["results"]:
        lines.extend(
            [
                f"### {result['scenario_name']}（{result['scenario_id']}）",
                "",
                f"- **strategy_type**：{result['strategy_type']}",
                f"- **目标指标**：{result['target_metric']} / M1 D7 recovery_rate_d7",
                f"- **target_anomaly_id**：{result['target_anomaly_id']}",
                f"- **baseline / scenario / estimated delta**：{_fmt(result['baseline_value'])} / {_fmt(result['scenario_value'])} / {_fmt(result['estimated_delta'])}",
                f"- **estimated_direction**：{result['estimated_direction']}",
                f"- **confidence**：{result['confidence']}",
                f"- **影响客群**：{_format_segments(result['impacted_segments'])}",
                f"- **业务解释**：{result['business_interpretation']}",
                f"- **推荐动作**：{result['recommended_action']}",
                f"- **caveats**：{'; '.join(result['caveats'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## 4. Business Boundary",
            "",
            *[f"- {item}" for item in report["business_boundary"]],
            "",
        ]
    )
    return "\n".join(lines)


def _evaluate_one(scenario: dict[str, Any], m3_summary: dict[str, Any]) -> dict[str, Any]:
    scenario_id = str(scenario["scenario_id"])
    rule = SCENARIO_RULES.get(scenario_id, {})
    evidence = _collect_evidence(scenario, m3_summary, str(rule.get("keyword", "")))
    baseline = _baseline_value(scenario, m3_summary, evidence)
    signal_found = bool(evidence)
    delta = float(rule.get("delta", 0.001)) if signal_found else 0.0
    direction = str(rule.get("direction", scenario.get("expected_direction", "monitor"))) if signal_found else "monitor"
    confidence = str(rule.get("confidence", "low")) if signal_found else "low"
    if direction == "monitor":
        scenario_value = baseline + delta
    elif direction in {"improve", "reduce_risk"}:
        scenario_value = baseline + delta
    else:
        scenario_value = baseline

    caveats = [
        "estimated_delta 是 demo estimate，不是真实预测。",
        "不改变 M1/M2/M3 指标口径。",
        str(rule.get("caveat", "该场景仅用于离线策略评估演示。")),
    ]
    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "strategy_type": scenario["strategy_type"],
        "target_metric": scenario["target_metric"],
        "target_anomaly_id": scenario["target_anomaly_id"],
        "baseline_value": round(baseline, 6),
        "scenario_value": round(min(max(scenario_value, 0.0), 1.0), 6),
        "estimated_delta": round(delta, 6),
        "estimated_direction": direction,
        "confidence": confidence,
        "impacted_segments": scenario["target_segments"],
        "assumptions_used": list(scenario.get("assumptions", [])),
        "evidence_links": evidence,
        "recommended_action": str(rule.get("recommended_action", "继续离线验证该策略场景。")),
        "business_interpretation": _business_interpretation(scenario_id),
        "compliance_boundary": list(scenario["compliance_boundary"]),
        "caveats": caveats,
    }


def _collect_evidence(scenario: dict[str, Any], m3_summary: dict[str, Any], keyword: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    target_anomaly_id = scenario.get("target_anomaly_id")
    for anomaly in m3_summary.get("high_priority_anomalies", []):
        if _matches_evidence(anomaly, keyword, target_anomaly_id):
            evidence.append(_evidence_item("anomaly", anomaly))
    target = _target_anomaly(m3_summary)
    if _matches_evidence(target, keyword, target_anomaly_id):
        evidence.append(_evidence_item("anomaly", target))
    for driver in m3_summary.get("m1_d7_attribution_summary", {}).get("top_drivers", []):
        if _matches_evidence(driver, keyword, target_anomaly_id):
            evidence.append(_evidence_item("attribution", driver))
    for item in m3_summary.get("process_evidence", []):
        if _matches_evidence(item, keyword, target_anomaly_id):
            evidence.append(_evidence_item("process_evidence", item))
    return evidence[:6]


def _matches_evidence(item: dict[str, Any], keyword: str, target_anomaly_id: Any) -> bool:
    if not isinstance(item, dict):
        return False
    values = {str(value) for value in item.values() if isinstance(value, (str, int, float))}
    text = " ".join(values)
    return bool((target_anomaly_id and str(target_anomaly_id) in text) or (keyword and keyword in text))


def _evidence_item(source: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": source,
        "source_id": item.get("anomaly_id") or item.get("attribution_id") or item.get("source_id"),
        "metric_code": item.get("metric_code"),
        "driver": item.get("driver") or _dimension_label(item),
        "baseline_value": item.get("baseline_value"),
        "recent_value": item.get("recent_value"),
        "delta": item.get("delta") if "delta" in item else item.get("absolute_change"),
        "note": item.get("explanation") or item.get("business_interpretation") or item.get("recommended_next_step"),
    }


def _baseline_value(scenario: dict[str, Any], m3_summary: dict[str, Any], evidence: list[dict[str, Any]]) -> float:
    target_anomaly_id = scenario.get("target_anomaly_id")
    if isinstance(target_anomaly_id, str) and target_anomaly_id.startswith("M3B-"):
        for item in evidence:
            if item.get("source_id") == target_anomaly_id and isinstance(item.get("recent_value"), (int, float)):
                return float(item["recent_value"])
    target = _target_anomaly(m3_summary)
    if isinstance(target.get("recent_value"), (int, float)):
        return float(target["recent_value"])
    return 0.0


def _target_anomaly(m3_summary: dict[str, Any]) -> dict[str, Any]:
    target = m3_summary.get("attribution_target_anomaly")
    if isinstance(target, dict):
        return target
    nested = m3_summary.get("m1_d7_attribution_summary", {}).get("target_anomaly")
    return nested if isinstance(nested, dict) else {}


def _business_interpretation(scenario_id: str) -> str:
    return {
        "increase_ai_call_coverage": "AI 外呼覆盖下降是 contact weakness 线索，离线模拟只评估触达补强可能带来的方向性改善。",
        "increase_manual_capacity": "人均案量上升说明产能压力变大，离线模拟只评估补人工后是否可能缓解 M1 D7 压力。",
        "adjust_reduction_usage": "减免使用率下降提示 settlement tool 可能使用不足，离线模拟只观察回收改善方向。",
        "vendor_reallocation": "资源再分配围绕 channel / vendor / line / region 信号展开，用于评估资源组合调整的影响面。",
        "score_band_D_priority": "score_band=D 是高风险分层线索，离线模拟只评估提高跟进优先级的方向性价值。",
    }.get(scenario_id, "该策略场景用于离线 demo estimate。")


def _dimension_label(item: dict[str, Any]) -> str:
    if item.get("dimension_name") and item.get("dimension_value"):
        return f"{item['dimension_name']}={item['dimension_value']}"
    return ""


def _format_segments(segments: list[dict[str, Any]]) -> str:
    return ", ".join(f"{item.get('dimension')}={item.get('value')}" for item in segments)


def _fmt(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.4%}"
    return str(value)
