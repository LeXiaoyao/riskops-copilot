"""M6-C1 ROI calculator for offline strategy demo estimates."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPORT_VERSION = "m6-c1-v1"
DEFAULT_ASSUMPTIONS = {
    "assumed_case_base": 10000,
    "unit_recovery_value": 500,
    "ai_call_unit_cost": 0.08,
    "manual_capacity_unit_cost": 8.0,
    "reduction_cost_rate": 0.15,
    "vendor_reallocation_admin_cost": 3000,
    "segmentation_priority_admin_cost": 2000,
    "payback_window_days": 30,
}
DEMO_DISCLAIMER = (
    "This ROI calculator uses synthetic data only and demo cost assumptions. "
    "It creates no real financial conclusion and no real collection action."
)
BOUNDARY_TEXT = [
    "synthetic data only",
    "demo cost assumptions",
    "no real customer data",
    "no real financial conclusion",
    "no real collection action",
    "no SMS / voice / WhatsApp",
    "no LLM decisioning",
]
RESULT_REQUIRED_FIELDS = [
    "scenario_id",
    "scenario_name",
    "strategy_type",
    "target_metric",
    "estimated_delta",
    "assumed_case_base",
    "unit_recovery_value",
    "gross_benefit",
    "action_cost",
    "net_benefit",
    "roi_ratio",
    "payback_period_days",
    "cost_formula",
    "benefit_formula",
    "cost_assumption",
]


def load_strategy_eval_results(path: str | Path) -> dict[str, Any]:
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(f"Strategy evaluation results not found: {input_path}")
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Strategy evaluation results are invalid JSON: {input_path}. Error: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Strategy evaluation results must be a JSON object: {input_path}")
    if not isinstance(payload.get("results"), list):
        raise ValueError(f"Strategy evaluation results must contain a results list: {input_path}")
    return payload


def calculate_roi_results(strategy_eval_results: dict[str, Any]) -> dict[str, Any]:
    source_results = strategy_eval_results.get("results", [])
    if not isinstance(source_results, list):
        raise ValueError("Strategy evaluation results must contain a results list.")

    results = [_calculate_one(item) for item in source_results]
    positive_results = [item for item in results if item["roi_ratio"] is not None and item["roi_ratio"] > 0]
    highest_roi = max(results, key=lambda item: item["roi_ratio"] if item["roi_ratio"] is not None else float("-inf"), default=None)
    return {
        "report_version": REPORT_VERSION,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_report_version": strategy_eval_results.get("report_version"),
        "demo_disclaimer": DEMO_DISCLAIMER,
        "cost_assumptions": dict(DEFAULT_ASSUMPTIONS),
        "scenario_count": len(results),
        "positive_roi_count": len(positive_results),
        "highest_roi_scenario": _highest_roi_summary(highest_roi),
        "results": results,
        "business_boundary": list(BOUNDARY_TEXT),
    }


def write_roi_outputs(results: dict[str, Any], output_json: str | Path, output_md: str | Path) -> None:
    json_path = Path(output_json)
    md_path = Path(output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_roi_markdown(results), encoding="utf-8")


def render_roi_markdown(results: dict[str, Any]) -> str:
    assumptions = results["cost_assumptions"]
    lines = [
        "# M6-C1 ROI Calculator Summary",
        "",
        "## 1. Demo Disclaimer",
        "",
        f"- {results['demo_disclaimer']}",
        *[f"- {item}" for item in BOUNDARY_TEXT],
        "",
        "## 2. demo cost assumptions",
        "",
        f"- **assumed_case_base**：{assumptions['assumed_case_base']}",
        f"- **unit_recovery_value**：{_money(assumptions['unit_recovery_value'])}",
        f"- **ai_call_unit_cost**：{_money(assumptions['ai_call_unit_cost'])}",
        f"- **manual_capacity_unit_cost**：{_money(assumptions['manual_capacity_unit_cost'])}",
        f"- **reduction_cost_rate**：{_ratio(assumptions['reduction_cost_rate'])}",
        f"- **vendor_reallocation_admin_cost**：{_money(assumptions['vendor_reallocation_admin_cost'])}",
        f"- **segmentation_priority_admin_cost**：{_money(assumptions['segmentation_priority_admin_cost'])}",
        f"- **payback_window_days**：{assumptions['payback_window_days']}",
        "",
        "## 3. Executive Summary",
        "",
        f"- **scenario count**：{results['scenario_count']}",
        f"- **positive ROI scenarios**：{results['positive_roi_count']}",
        f"- **highest ROI scenario**：{_highest_roi_label(results.get('highest_roi_scenario'))}",
        "",
        "## 4. Scenario ROI Results",
        "",
    ]
    for item in results["results"]:
        lines.extend(
            [
                f"### {item['scenario_name']}（{item['scenario_id']}）",
                "",
                f"- **strategy_type**：{item['strategy_type']}",
                f"- **estimated_delta**：{_ratio(item['estimated_delta'])}",
                f"- **gross_benefit**：{_money(item['gross_benefit'])}",
                f"- **action_cost**：{_money(item['action_cost'])}",
                f"- **net_benefit**：{_money(item['net_benefit'])}",
                f"- **roi_ratio**：{_number(item['roi_ratio'])}",
                f"- **payback_period_days**：{_number(item['payback_period_days'])}",
                f"- **benefit_formula**：{item['benefit_formula']}",
                f"- **cost_formula**：{item['cost_formula']}",
                "",
            ]
        )
    return "\n".join(lines)


def _calculate_one(result: dict[str, Any]) -> dict[str, Any]:
    strategy_type = str(result.get("strategy_type", ""))
    estimated_delta = float(result.get("estimated_delta", 0.0))
    assumed_case_base = float(DEFAULT_ASSUMPTIONS["assumed_case_base"])
    unit_recovery_value = float(DEFAULT_ASSUMPTIONS["unit_recovery_value"])
    gross_benefit = estimated_delta * assumed_case_base * unit_recovery_value
    action_cost, cost_formula, cost_assumption = _action_cost(strategy_type, gross_benefit)
    net_benefit = gross_benefit - action_cost
    roi_ratio = net_benefit / action_cost if action_cost else None
    payback_period_days = (
        action_cost / gross_benefit * float(DEFAULT_ASSUMPTIONS["payback_window_days"]) if gross_benefit else None
    )
    return {
        "scenario_id": result.get("scenario_id"),
        "scenario_name": result.get("scenario_name"),
        "strategy_type": strategy_type,
        "target_metric": result.get("target_metric"),
        "estimated_delta": round(estimated_delta, 6),
        "assumed_case_base": int(DEFAULT_ASSUMPTIONS["assumed_case_base"]),
        "unit_recovery_value": DEFAULT_ASSUMPTIONS["unit_recovery_value"],
        "gross_benefit": round(gross_benefit, 2),
        "action_cost": round(action_cost, 2),
        "net_benefit": round(net_benefit, 2),
        "roi_ratio": round(roi_ratio, 6) if roi_ratio is not None else None,
        "payback_period_days": round(payback_period_days, 2) if payback_period_days is not None else None,
        "cost_formula": cost_formula,
        "benefit_formula": "estimated_delta × assumed_case_base × unit_recovery_value",
        "cost_assumption": cost_assumption,
    }


def _action_cost(strategy_type: str, gross_benefit: float) -> tuple[float, str, str]:
    if strategy_type == "contact_strategy":
        return (
            float(DEFAULT_ASSUMPTIONS["assumed_case_base"]) * float(DEFAULT_ASSUMPTIONS["ai_call_unit_cost"]),
            "assumed_case_base × ai_call_unit_cost",
            "AI call unit cost applied to assumed case base.",
        )
    if strategy_type == "capacity_strategy":
        return (
            float(DEFAULT_ASSUMPTIONS["assumed_case_base"]) * 0.1 * float(DEFAULT_ASSUMPTIONS["manual_capacity_unit_cost"]),
            "assumed_case_base × 0.1 × manual_capacity_unit_cost",
            "Manual capacity cost assumes 10% of cases need capacity handling.",
        )
    if strategy_type == "settlement_strategy":
        return (
            gross_benefit * float(DEFAULT_ASSUMPTIONS["reduction_cost_rate"]),
            "gross_benefit × reduction_cost_rate",
            "Settlement cost uses demo reduction cost rate.",
        )
    if strategy_type == "allocation_strategy":
        return (
            float(DEFAULT_ASSUMPTIONS["vendor_reallocation_admin_cost"]),
            "vendor_reallocation_admin_cost",
            "Vendor reallocation uses fixed demo admin cost.",
        )
    if strategy_type == "segmentation_strategy":
        return (
            float(DEFAULT_ASSUMPTIONS["segmentation_priority_admin_cost"]),
            "segmentation_priority_admin_cost",
            "Segmentation priority uses fixed demo admin cost.",
        )
    return 0.0, "unknown_strategy_type", "No demo cost assumption is defined for this strategy type."


def _highest_roi_summary(result: dict[str, Any] | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "scenario_id": result["scenario_id"],
        "scenario_name": result["scenario_name"],
        "strategy_type": result["strategy_type"],
        "roi_ratio": result["roi_ratio"],
    }


def _highest_roi_label(summary: dict[str, Any] | None) -> str:
    if not summary:
        return "none"
    return f"{summary['scenario_name']} / {summary['scenario_id']} / roi_ratio={_number(summary['roi_ratio'])}"


def _money(value: float) -> str:
    return f"{value:,.2f}"


def _ratio(value: float) -> str:
    return f"{value:.4%}"


def _number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}"
