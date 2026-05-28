"""RiskOps Copilot demo CLI entry point."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, TextIO

from riskops.engines.copilot.briefing_builder import (
    build_copilot_briefing,
    write_copilot_briefing,
    write_copilot_briefing_with_narrative,
)
from riskops.engines.dashboard import DashboardInputError, write_dashboard
from riskops.engines.model_lab.ml_readiness import assess_ml_readiness, write_ml_readiness_outputs
from riskops.engines.model_lab.roi_calculator import calculate_roi_results, load_strategy_eval_results, write_roi_outputs
from riskops.engines.model_lab.scenario_schema import (
    load_strategy_scenarios,
    summarize_strategy_scenarios,
    validate_strategy_scenarios,
)
from riskops.engines.model_lab.strategy_evaluator import run_strategy_evaluation
from riskops.engines.qc import scan_batch, scan_text_with_llm
from riskops.engines.report import (
    BusinessReportInputError,
    write_business_report,
    write_business_report_excel,
    write_business_report_ppt,
)
from riskops.engines.script import approve_and_log, check_frequency, generate_script_draft, load_case_context
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

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M3_SUMMARY = ROOT / "outputs" / "m3" / "m3_summary.json"
DEFAULT_DASHBOARD = ROOT / "outputs" / "dashboard" / "dashboard.html"
DEFAULT_REPORT_MD = ROOT / "outputs" / "reports" / "m4_business_report.md"
DEFAULT_REPORT_HTML = ROOT / "outputs" / "reports" / "m4_business_report.html"
DEFAULT_REPORT_XLSX = ROOT / "outputs" / "reports" / "m4_business_report.xlsx"
DEFAULT_REPORT_PPTX = ROOT / "outputs" / "reports" / "m4_business_report.pptx"
DEFAULT_STRATEGY_SCENARIOS = ROOT / "configs" / "strategy_scenarios.yaml"
DEFAULT_STRATEGY_EVAL_JSON = ROOT / "outputs" / "model_lab" / "strategy_eval_results.json"
DEFAULT_STRATEGY_EVAL_MD = ROOT / "outputs" / "model_lab" / "strategy_eval_summary.md"
DEFAULT_ROI_JSON = ROOT / "outputs" / "model_lab" / "roi_results.json"
DEFAULT_ROI_MD = ROOT / "outputs" / "model_lab" / "roi_summary.md"
DEFAULT_SYNTHETIC_DATA = ROOT / "synthetic_data"
DEFAULT_ML_READINESS_JSON = ROOT / "outputs" / "model_lab" / "ml_baseline" / "readiness.json"
DEFAULT_ML_READINESS_MD = ROOT / "docs" / "m6_ml_readiness.md"
DEFAULT_ML_BASELINE_DIR = ROOT / "outputs" / "model_lab" / "ml_baseline"
DEFAULT_ML_METRICS_JSON = DEFAULT_ML_BASELINE_DIR / "metrics.json"
DEFAULT_COPILOT_BRIEFING = ROOT / "outputs" / "copilot" / "briefing.md"
DEFAULT_VISUALIZATION_DIR = ROOT / "outputs" / "visualization"
DEFAULT_ANOMALY_SEVERITY_CHART = DEFAULT_VISUALIZATION_DIR / "anomaly_severity.html"
DEFAULT_DRIVER_CONTRIBUTION_CHART = DEFAULT_VISUALIZATION_DIR / "driver_contribution.html"
DEFAULT_ROI_COMPARISON_CHART = DEFAULT_VISUALIZATION_DIR / "roi_comparison.html"
DEFAULT_COLLECTION_FUNNEL_CHART = DEFAULT_VISUALIZATION_DIR / "collection_funnel.html"
DEFAULT_WATERFALL_CHART = DEFAULT_VISUALIZATION_DIR / "waterfall.html"
DEFAULT_VENDOR_MATRIX_CHART = DEFAULT_VISUALIZATION_DIR / "vendor_matrix.html"
DEFAULT_CAPACITY_HEATMAP_CHART = DEFAULT_VISUALIZATION_DIR / "capacity_heatmap.html"
DEFAULT_DPD_STRUCTURE_CHART = DEFAULT_VISUALIZATION_DIR / "dpd_structure.html"
DEFAULT_REDUCTION_ROI_CHART = DEFAULT_VISUALIZATION_DIR / "reduction_roi.html"
DEFAULT_COMPLAINT_RISK_CHART = DEFAULT_VISUALIZATION_DIR / "complaint_risk.html"
RUN_ML_BASELINE = ROOT / "scripts" / "run_ml_baseline.py"

OUTPUT_PATHS = [
    DEFAULT_DASHBOARD,
    DEFAULT_REPORT_MD,
    DEFAULT_REPORT_HTML,
    DEFAULT_REPORT_XLSX,
    DEFAULT_REPORT_PPTX,
    ROOT / "outputs" / "m3" / "m3_summary.md",
    DEFAULT_M3_SUMMARY,
    DEFAULT_STRATEGY_EVAL_JSON,
    DEFAULT_STRATEGY_EVAL_MD,
    DEFAULT_ROI_JSON,
    DEFAULT_ROI_MD,
    DEFAULT_ML_READINESS_JSON,
    DEFAULT_ML_METRICS_JSON,
    DEFAULT_ML_BASELINE_DIR / "feature_importance.csv",
    DEFAULT_COPILOT_BRIEFING,
    DEFAULT_ANOMALY_SEVERITY_CHART,
    DEFAULT_DRIVER_CONTRIBUTION_CHART,
    DEFAULT_ROI_COMPARISON_CHART,
    DEFAULT_COLLECTION_FUNNEL_CHART,
    DEFAULT_WATERFALL_CHART,
    DEFAULT_VENDOR_MATRIX_CHART,
    DEFAULT_CAPACITY_HEATMAP_CHART,
    DEFAULT_DPD_STRUCTURE_CHART,
    DEFAULT_REDUCTION_ROI_CHART,
    DEFAULT_COMPLAINT_RISK_CHART,
]

COMMON_COMMANDS = [
    "python scripts/riskops_cli.py summary",
    "python scripts/riskops_cli.py anomalies",
    "python scripts/riskops_cli.py drivers",
    "python scripts/riskops_cli.py outputs",
    "python scripts/riskops_cli.py scenarios",
    "python scripts/riskops_cli.py strategy-eval",
    "python scripts/riskops_cli.py roi",
    "python scripts/riskops_cli.py model-lab",
    "python scripts/riskops_cli.py ml-readiness",
    "python scripts/riskops_cli.py ml-baseline",
    "python scripts/riskops_cli.py briefing",
    "python scripts/riskops_cli.py qc-scan --texts \"你赶快还钱\" \"我是法院，马上起诉你\"",
    "python scripts/riskops_cli.py render-model-lab",
    "python scripts/riskops_cli.py render-dashboard",
    "python scripts/riskops_cli.py render-report",
    "python scripts/riskops_cli.py render-excel",
    "python scripts/riskops_cli.py render-ppt",
    "python scripts/riskops_cli.py render-charts",
    "python scripts/riskops_cli.py script --case-id CASE00000001 --channel sms",
    "python scripts/riskops_cli.py tui",
    # C3 DONE
]


class CliInputError(RuntimeError):
    """Raised when CLI input files are missing or malformed."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RiskOps Copilot demo CLI — M6 model lab + M7 state recovery feasibility guard (synthetic data only).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="Show current project status and M3/M4 output summary.")
    _add_input_arg(summary)
    summary.set_defaults(handler=_handle_summary)

    anomalies = subparsers.add_parser("anomalies", help="Show high-priority anomaly list.")
    _add_input_arg(anomalies)
    anomalies.set_defaults(handler=_handle_anomalies)

    drivers = subparsers.add_parser("drivers", help="Show M1 D7 recovery decline top drivers.")
    _add_input_arg(drivers)
    drivers.set_defaults(handler=_handle_drivers)

    outputs = subparsers.add_parser("outputs", help="Show dashboard, report, and M3 output paths.")
    outputs.set_defaults(handler=_handle_outputs)

    scenarios = subparsers.add_parser("scenarios", help="Show M6-A strategy scenarios.")
    scenarios.add_argument("--config", type=Path, default=DEFAULT_STRATEGY_SCENARIOS)
    scenarios.set_defaults(handler=_handle_scenarios)

    strategy_eval = subparsers.add_parser("strategy-eval", help="Show M6-B offline strategy evaluation summary.")
    strategy_eval.add_argument("--input", type=Path, default=DEFAULT_STRATEGY_EVAL_JSON)
    strategy_eval.set_defaults(handler=_handle_strategy_eval)

    roi = subparsers.add_parser("roi", help="Show M6-C ROI cost-benefit summary.")
    roi.add_argument("--input", type=Path, default=DEFAULT_ROI_JSON)
    roi.set_defaults(handler=_handle_roi)

    model_lab = subparsers.add_parser("model-lab", help="Show M6 model lab overview and output paths.")
    model_lab.add_argument("--scenarios", type=Path, default=DEFAULT_STRATEGY_SCENARIOS)
    model_lab.add_argument("--strategy-eval", type=Path, default=DEFAULT_STRATEGY_EVAL_JSON)
    model_lab.add_argument("--roi", type=Path, default=DEFAULT_ROI_JSON)
    model_lab.set_defaults(handler=_handle_model_lab)

    ml_readiness = subparsers.add_parser("ml-readiness", help="Assess M6-D ML target readiness.")
    ml_readiness.add_argument("--data-dir", type=Path, default=DEFAULT_SYNTHETIC_DATA)
    ml_readiness.add_argument("--output-json", type=Path, default=DEFAULT_ML_READINESS_JSON)
    ml_readiness.add_argument("--output-md", type=Path, default=DEFAULT_ML_READINESS_MD)
    ml_readiness.set_defaults(handler=_handle_ml_readiness)

    ml_baseline = subparsers.add_parser("ml-baseline", help="Run M6-D leakage-safe ML baseline.")
    ml_baseline.add_argument("--data-dir", type=Path, default=DEFAULT_SYNTHETIC_DATA)
    ml_baseline.add_argument("--output-dir", type=Path, default=DEFAULT_ML_BASELINE_DIR)
    ml_baseline.add_argument("--target", choices=["any_payment", "state_recovery"], default="any_payment")
    ml_baseline.add_argument("--model", choices=["logistic", "random_forest", "both"], default="both")
    ml_baseline.add_argument("--test-size", type=float, default=0.25)
    ml_baseline.add_argument("--random-seed", type=int, default=20260521)
    ml_baseline.add_argument("--exclude-vintage-month", action="store_true")
    ml_baseline.set_defaults(handler=_handle_ml_baseline)

    briefing = subparsers.add_parser("briefing", help="Render Copilot briefing (deterministic; add --use-llm for AI narrative).")
    briefing.add_argument("--m3-summary", type=Path, default=DEFAULT_M3_SUMMARY)
    briefing.add_argument("--strategy-eval", type=Path, default=DEFAULT_STRATEGY_EVAL_JSON)
    briefing.add_argument("--roi", type=Path, default=DEFAULT_ROI_JSON)
    briefing.add_argument("--ml-metrics", type=Path, default=DEFAULT_ML_METRICS_JSON)
    briefing.add_argument("--ml-readiness", type=Path, default=DEFAULT_ML_READINESS_JSON)
    briefing.add_argument("--output", type=Path, default=DEFAULT_COPILOT_BRIEFING)
    briefing.add_argument("--use-llm", action="store_true", help="Prepend AI narrative via DeepSeek API.")
    briefing.add_argument("--api-key", type=str, default=None, help="DeepSeek API key (default: $DEEPSEEK_API_KEY).")
    briefing.add_argument("--model", type=str, default="deepseek-chat", help="DeepSeek model name.")
    briefing.set_defaults(handler=_handle_briefing)

    tui = subparsers.add_parser("tui", help="Start the DeepSeek-style RiskOps Copilot TUI.")
    tui.set_defaults(handler=_handle_tui)

    qc_scan = subparsers.add_parser("qc-scan", help="Run compliance scan (keyword-only or keyword + LLM 11-dimension scoring).")
    qc_input = qc_scan.add_mutually_exclusive_group(required=True)
    qc_input.add_argument("--texts", nargs="+", help="Collection script texts to scan.")
    qc_input.add_argument("--file", type=Path, help="Text file path; one script per line.")
    qc_scan.add_argument("--use-llm", action="store_true", help="Append LLM 11-dimension scoring via DeepSeek API.")
    qc_scan.add_argument("--api-key", type=str, default=None, help="DeepSeek API key (default: $DEEPSEEK_API_KEY).")
    qc_scan.add_argument("--model", type=str, default="deepseek-chat", help="DeepSeek model name.")
    qc_scan.set_defaults(handler=_handle_qc_scan)

    script = subparsers.add_parser("script", help="Generate a mock compliant collection script draft.")
    script.add_argument("--case-id", required=True, help="Case id, for example CASE00000001 or CASE-00001.")
    script.add_argument("--channel", choices=["sms", "ai_call", "manual"], default="sms")
    script.add_argument("--approve", action="store_true", help="Mock approve and append an audit log record.")
    script.add_argument("--use-llm", action="store_true", help="Use DeepSeek to polish the deterministic draft.")
    script.set_defaults(handler=_handle_script)

    render_model_lab = subparsers.add_parser("render-model-lab", help="Render M6 strategy eval and ROI outputs.")
    render_model_lab.add_argument("--scenarios", type=Path, default=DEFAULT_STRATEGY_SCENARIOS)
    render_model_lab.add_argument("--m3-summary", type=Path, default=DEFAULT_M3_SUMMARY)
    render_model_lab.add_argument("--strategy-eval-json", type=Path, default=DEFAULT_STRATEGY_EVAL_JSON)
    render_model_lab.add_argument("--strategy-eval-md", type=Path, default=DEFAULT_STRATEGY_EVAL_MD)
    render_model_lab.add_argument("--roi-json", type=Path, default=DEFAULT_ROI_JSON)
    render_model_lab.add_argument("--roi-md", type=Path, default=DEFAULT_ROI_MD)
    render_model_lab.set_defaults(handler=_handle_render_model_lab)

    render_dashboard = subparsers.add_parser("render-dashboard", help="Render outputs/dashboard/dashboard.html.")
    _add_input_arg(render_dashboard)
    render_dashboard.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DASHBOARD,
        help="Dashboard HTML output path.",
    )
    render_dashboard.set_defaults(handler=_handle_render_dashboard)

    render_report = subparsers.add_parser(
        "render-report",
        help="Render outputs/reports/m4_business_report.md and .html.",
    )
    _add_input_arg(render_report)
    render_report.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_MD,
        help="Business report Markdown output path.",
    )
    render_report.add_argument(
        "--html-output",
        type=Path,
        default=DEFAULT_REPORT_HTML,
        help="Business report HTML output path.",
    )
    render_report.set_defaults(handler=_handle_render_report)

    render_excel = subparsers.add_parser(
        "render-excel",
        help="Render outputs/reports/m4_business_report.xlsx.",
    )
    _add_input_arg(render_excel)
    render_excel.add_argument(
        "--roi-input",
        type=Path,
        default=DEFAULT_ROI_JSON,
        help="Path to ROI results JSON.",
    )
    render_excel.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_XLSX,
        help="Business report Excel output path.",
    )
    render_excel.set_defaults(handler=_handle_render_excel)

    render_ppt = subparsers.add_parser(
        "render-ppt",
        help="Render outputs/reports/m4_business_report.pptx.",
    )
    _add_input_arg(render_ppt)
    render_ppt.add_argument(
        "--roi-input",
        type=Path,
        default=DEFAULT_ROI_JSON,
        help="Path to ROI results JSON.",
    )
    render_ppt.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PPTX,
        help="Business report PowerPoint output path.",
    )
    render_ppt.set_defaults(handler=_handle_render_ppt)

    render_charts = subparsers.add_parser("render-charts", help="Render offline Plotly charts to outputs/visualization/*.html.")
    render_charts.add_argument("--m3-summary", type=Path, default=DEFAULT_M3_SUMMARY)
    render_charts.add_argument("--roi", type=Path, default=DEFAULT_ROI_JSON)
    render_charts.add_argument("--output-dir", type=Path, default=DEFAULT_VISUALIZATION_DIR)
    render_charts.set_defaults(handler=_handle_render_charts)

    return parser


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    args = build_parser().parse_args(argv)
    try:
        args.handler(args, stdout)
    except CliInputError as exc:
        print(f"riskops_cli failed: {exc}", file=stderr)
        return 2
    return 0


def _add_input_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_M3_SUMMARY,
        help="Path to M3 summary JSON.",
    )


def _handle_summary(args: argparse.Namespace, out: TextIO) -> None:
    summary = _load_summary(args.input)
    overview = _as_dict(summary.get("anomaly_overview"))
    severity_counts = _as_dict(overview.get("severity_counts"))
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))

    _print_title(out, "RiskOps Copilot")
    print("- 当前阶段：M6/M7 RiskOps demo — model lab + state recovery feasibility guard", file=out)
    print("- 当前 demo 数据边界：synthetic data / 合成数据，不接真实数据，不接 LLM。", file=out)
    print("- anomaly 总数：{}".format(_safe_int(overview.get("anomaly_count"))), file=out)
    print("- high / medium / low：{} / {} / {}".format(
        _safe_int(severity_counts.get("high")),
        _safe_int(severity_counts.get("medium")),
        _safe_int(severity_counts.get("low")),
    ), file=out)
    print("- attribution target metric：{}（{}）".format(
        attribution.get("target_metric_name_cn") or "D7 回收率",
        attribution.get("target_metric_code") or "recovery_rate_d7",
    ), file=out)
    print("- dashboard 路径：{}".format(_display_path(DEFAULT_DASHBOARD)), file=out)
    print("- business report 路径：{}".format(_display_path(DEFAULT_REPORT_MD)), file=out)
    print("- business report HTML：{}".format(_display_path(DEFAULT_REPORT_HTML)), file=out)
    print("", file=out)
    _print_common_commands(out)


def _handle_anomalies(args: argparse.Namespace, out: TextIO) -> None:
    summary = _load_summary(args.input)
    anomalies = [item for item in _as_list(summary.get("high_priority_anomalies")) if isinstance(item, dict)]

    _print_title(out, "高优先级异常列表")
    if not anomalies:
        print("- 未发现 high priority anomalies。", file=out)
        return

    for index, anomaly in enumerate(anomalies, start=1):
        print(f"{index}. {anomaly.get('metric_name_cn')}（{anomaly.get('metric_code')}）", file=out)
        print(f"   - metric name：{anomaly.get('metric_name_cn')}", file=out)
        print(f"   - severity：{anomaly.get('severity')}", file=out)
        print(
            "   - dimension：{}={}".format(
                anomaly.get("dimension_name"),
                anomaly.get("dimension_value"),
            ),
            file=out,
        )
        print("   - baseline：{}".format(_format_metric_value(anomaly)), file=out)
        print("   - recent：{}".format(_format_metric_value(anomaly, key="recent_value")), file=out)
        print("   - relative change：{}".format(_format_pct(anomaly.get("relative_change"), signed=True)), file=out)
        print("   - recommended next step：{}".format(anomaly.get("recommended_next_step")), file=out)


def _handle_drivers(args: argparse.Namespace, out: TextIO) -> None:
    summary = _load_summary(args.input)
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))
    target = _as_dict(attribution.get("target_anomaly")) or _as_dict(summary.get("attribution_target_anomaly"))
    drivers = [item for item in _as_list(attribution.get("top_drivers")) if isinstance(item, dict)][:5]

    _print_title(out, "M1 D7 回收率下降专题")
    print("- target metric：{}（{}）".format(
        attribution.get("target_metric_name_cn") or "D7 回收率",
        attribution.get("target_metric_code") or "recovery_rate_d7",
    ), file=out)
    if target:
        print("- baseline / recent：{} / {}".format(
            _format_metric_value(target),
            _format_metric_value(target, key="recent_value"),
        ), file=out)
        print("- relative change：{}".format(_format_pct(target.get("relative_change"), signed=True)), file=out)
    print("", file=out)
    print("业务口径边界：", file=out)
    print("- channel_code=ECOM、province=山东/上海、score_band=D/A 是归因线索，不是最终根因。", file=out)
    print("- line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路。", file=out)
    print("- 人均案量是 capacity pressure signal，不是最终根因。", file=out)
    print("- process evidence 是过程证据，不是单独根因。", file=out)
    print("", file=out)
    print("Top 5 drivers：", file=out)
    if not drivers:
        print("- 未发现 drivers。", file=out)
        return

    for driver in drivers:
        rank = driver.get("rank") or "?"
        name = "{}={}".format(driver.get("dimension_name"), driver.get("dimension_value"))
        role, driver_type = _driver_role_and_type(driver)
        print(f"{rank}. {name}", file=out)
        print("   - contribution score：{}".format(_format_pct(driver.get("contribution_score"))), file=out)
        print(f"   - role / type：{role} / {driver_type}", file=out)
        print("   - baseline / recent：{} / {}".format(
            _format_metric_value(driver),
            _format_metric_value(driver, key="recent_value"),
        ), file=out)
        print("   - business interpretation：{}".format(driver.get("business_interpretation")), file=out)
        print("   - recommended action：{}".format(driver.get("recommended_action")), file=out)


def _handle_outputs(_args: argparse.Namespace, out: TextIO) -> None:
    _print_title(out, "输出路径")
    for path in OUTPUT_PATHS:
        status = "exists" if path.exists() else "missing"
        print(f"- {_display_path(path)}：{status}", file=out)


def _handle_scenarios(args: argparse.Namespace, out: TextIO) -> None:
    scenarios = _load_scenarios(args.config)
    summary = summarize_strategy_scenarios(scenarios)

    _print_title(out, "M6-A Strategy Scenarios")
    print(f"- scenario count：{summary['scenario_count']}", file=out)
    print(f"- target metric：{', '.join(summary['target_metric_counts'])}", file=out)
    print("- compliance boundary：synthetic data only / no real customer data / no real collection action / no SMS / voice / WhatsApp / no LLM decisioning", file=out)
    print("", file=out)
    for scenario in scenarios:
        print(f"- **scenario_id**：{scenario.get('scenario_id')}", file=out)
        print(f"  **strategy_type**：{scenario.get('strategy_type')}", file=out)
        print(f"  **target_metric**：{scenario.get('target_metric')}", file=out)
        print(f"  **description**：{scenario.get('description')}", file=out)
        print(f"  **boundary**：{_format_boundary(scenario.get('compliance_boundary'))}", file=out)


def _handle_strategy_eval(args: argparse.Namespace, out: TextIO) -> None:
    report = _load_json_object(args.input, "strategy evaluation results")
    results = [item for item in _as_list(report.get("results")) if isinstance(item, dict)]

    _print_title(out, "M6-B Offline Strategy Evaluation")
    print("- boundary：offline demo estimate，不是真实策略决策，不产生真实催收动作。", file=out)
    print(f"- scenario count：{_safe_int(report.get('scenario_count'))}", file=out)
    print(f"- target metric：{', '.join(_as_dict(report.get('target_metric_counts')).keys())}", file=out)
    print(f"- priority scenarios：{', '.join(str(item) for item in _as_list(report.get('priority_scenarios'))) or 'none'}", file=out)
    print("", file=out)
    for item in results:
        print(f"- {item.get('scenario_id')}：{item.get('estimated_direction')}", file=out)
        print(f"  **estimated_delta**：{_format_pct(item.get('estimated_delta'))}", file=out)
        print(f"  **confidence**：{item.get('confidence')}", file=out)
    print("", file=out)
    print("- synthetic data only", file=out)
    print("- no real customer data", file=out)
    print("- no LLM decisioning", file=out)


def _handle_roi(args: argparse.Namespace, out: TextIO) -> None:
    report = _load_json_object(args.input, "ROI results")
    highest = _as_dict(report.get("highest_roi_scenario"))
    results = [item for item in _as_list(report.get("results")) if isinstance(item, dict)]

    _print_title(out, "M6-C ROI Cost-Benefit")
    print("- boundary：demo cost assumptions，不是真实财务结论，不产生真实催收动作。", file=out)
    print(f"- scenario count：{_safe_int(report.get('scenario_count'))}", file=out)
    print(f"- positive ROI scenarios：{_safe_int(report.get('positive_roi_count'))}", file=out)
    print(f"- highest ROI scenario：{highest.get('scenario_id') or 'none'}", file=out)
    print("- demo cost assumptions：assumed_case_base / unit_recovery_value / ai_call_unit_cost / manual_capacity_unit_cost / reduction_cost_rate", file=out)
    print("", file=out)
    for item in results:
        print(f"- {item.get('scenario_id')}", file=out)
        print(f"  **gross benefit**：{_format_money(item.get('gross_benefit'))}", file=out)
        print(f"  **action cost**：{_format_money(item.get('action_cost'))}", file=out)
        print(f"  **net benefit**：{_format_money(item.get('net_benefit'))}", file=out)
        print(f"  **roi_ratio**：{_format_number(item.get('roi_ratio'))}", file=out)
    print("", file=out)
    print("- synthetic data only", file=out)
    print("- no real customer data", file=out)
    print("- no real financial conclusion", file=out)


def _handle_model_lab(args: argparse.Namespace, out: TextIO) -> None:
    scenarios = _load_scenarios(args.scenarios)
    scenario_summary = summarize_strategy_scenarios(scenarios)
    strategy_eval = _load_json_object(args.strategy_eval, "strategy evaluation results")
    roi = _load_json_object(args.roi, "ROI results")
    highest = _as_dict(roi.get("highest_roi_scenario"))
    priority = _as_list(strategy_eval.get("priority_scenarios"))
    top_scenario = highest.get("scenario_id") or (str(priority[0]) if priority else "none")

    _print_title(out, "M6 Model Lab Overview")
    print("- M6-A scenario schema：ready", file=out)
    print(f"- M6-B strategy eval output：{_display_path(args.strategy_eval)}", file=out)
    print(f"- M6-B strategy eval summary：{_display_path(DEFAULT_STRATEGY_EVAL_MD)}", file=out)
    print(f"- M6-C ROI output：{_display_path(args.roi)}", file=out)
    print(f"- M6-C ROI summary：{_display_path(DEFAULT_ROI_MD)}", file=out)
    print(f"- scenario count：{scenario_summary['scenario_count']}", file=out)
    print(f"- target metric：{', '.join(scenario_summary['target_metric_counts'])}", file=out)
    print(f"- top recommended scenario：{top_scenario}", file=out)
    print("", file=out)
    print("demo boundary：", file=out)
    print("- synthetic data only", file=out)
    print("- no real customer data", file=out)
    print("- no real collection action", file=out)
    print("- no SMS / voice / WhatsApp", file=out)
    print("- no LLM decisioning", file=out)


def _handle_ml_readiness(args: argparse.Namespace, out: TextIO) -> None:
    try:
        readiness = assess_ml_readiness(args.data_dir)
        paths = write_ml_readiness_outputs(readiness, args.output_json, args.output_md)
    except (FileNotFoundError, ValueError) as exc:
        raise CliInputError(exc) from exc

    _print_title(out, "M6-D ML Readiness")
    print(f"- recommended target：{readiness['recommended_target']}", file=out)
    print(f"- reason：{readiness['recommendation_reason']}", file=out)
    print(f"- readiness json：{_display_path(Path(paths['readiness_json']))}", file=out)
    print(f"- readiness report：{_display_path(Path(paths['readiness_report']))}", file=out)
    print("- synthetic data only", file=out)
    print("- no real customer data", file=out)
    print("- no PII in model features", file=out)
    print("- no automated decisioning", file=out)
    print("PASS ML readiness", file=out)


def _handle_ml_baseline(args: argparse.Namespace, out: TextIO) -> None:
    command = [
        sys.executable,
        str(RUN_ML_BASELINE),
        "--data-dir",
        str(args.data_dir),
        "--output-dir",
        str(args.output_dir),
        "--target",
        args.target,
        "--model",
        args.model,
        "--test-size",
        str(args.test_size),
        "--random-seed",
        str(args.random_seed),
    ]
    if args.exclude_vintage_month:
        command.append("--exclude-vintage-month")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout.rstrip(), file=out)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown ML baseline failure"
        raise CliInputError(detail)


def _handle_briefing(args: argparse.Namespace, out: TextIO) -> None:
    try:
        briefing = build_copilot_briefing(
            args.m3_summary,
            args.strategy_eval,
            args.roi,
            args.ml_metrics,
            args.ml_readiness,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        raise CliInputError(exc) from exc

    use_llm = getattr(args, "use_llm", False)
    narrative: str | None = None

    if use_llm:
        from riskops.engines.copilot.llm_narrator import narrate_briefing  # noqa: PLC0415
        print("calling DeepSeek API …", file=out)
        try:
            narrative = narrate_briefing(
                briefing,
                api_key=getattr(args, "api_key", None),
                model=getattr(args, "model", "deepseek-chat"),
            )
        except Exception as exc:  # noqa: BLE001
            print(f"LLM call failed ({exc})，falling back to deterministic briefing", file=out)
            narrative = None

    try:
        if narrative:
            output = write_copilot_briefing_with_narrative(briefing, narrative, args.output)
        else:
            output = write_copilot_briefing(briefing, args.output)
    except OSError as exc:
        raise CliInputError(exc) from exc

    what_happened = briefing["what_happened"]
    ml = briefing["ml_baseline"]
    print("Copilot briefing：{}".format(_display_path(Path(output))), file=out)
    print(f"- anomaly_count：{what_happened['anomaly_count']}", file=out)
    print(f"- target_metric：{what_happened['target_metric']}", file=out)
    print(f"- ml_target：{ml['recommended_target']}", file=out)
    print(f"- mode：{'llm+deterministic' if narrative else 'deterministic only'}", file=out)
    print("- no LLM automatic decisioning", file=out)
    print("- synthetic data only", file=out)
    print("PASS briefing", file=out)


def _handle_tui(_args: argparse.Namespace, out: TextIO) -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("请先设置 export DEEPSEEK_API_KEY=your_key", file=out)
        return
    from riskops.tui.app import RiskOpsTUIApp  # noqa: PLC0415

    RiskOpsTUIApp(api_key=api_key).run()


def _handle_qc_scan(args: argparse.Namespace, out: TextIO) -> None:
    if args.file:
        if not args.file.exists():
            raise CliInputError(f"qc-scan 输入文件不存在：{args.file}")
        texts = args.file.read_text(encoding="utf-8").splitlines()
    else:
        texts = list(args.texts or [])

    use_llm = getattr(args, "use_llm", False)
    api_key: str | None = getattr(args, "api_key", None) or os.getenv("DEEPSEEK_API_KEY")
    model: str = getattr(args, "model", "deepseek-chat")

    if use_llm and not api_key:
        print("LLM scoring skipped: DEEPSEEK_API_KEY not found，falling back to keyword-only scan", file=out)
        use_llm = False

    if use_llm:
        _print_title(out, "QC 合规扫描（关键词 + LLM 11维评分）")
        for index, text in enumerate(texts, start=1):
            result = scan_text_with_llm(text, api_key, model)  # type: ignore[arg-type]
            dims = result.get("dimensions", {})
            overall = result.get("overall_compliance_score", "-")
            review = result.get("supervisor_review_required", False)
            fallback = result.get("_fallback", False)
            kw_level = result.get("keyword_risk_level", "clean")
            summary = result.get("risk_summary", "")
            print(f"{index}. keyword_risk：{kw_level}  overall_score：{overall}  主管复核：{'是' if review else '否'}{'  [LLM不可用，规则兜底]' if fallback else ''}", file=out)
            if dims:
                dim_str = "  ".join(f"{k}={v}" for k, v in dims.items())
                print(f"   维度：{dim_str}", file=out)
            if summary:
                print(f"   {summary}", file=out)
            alt = result.get("suggested_alternative")
            if alt:
                print(f"   建议：{alt}", file=out)
        print("", file=out)
        print(f"- 总条数：{len(texts)}", file=out)
        print("PASS qc-scan (llm)", file=out)
    else:
        results = scan_batch(texts)
        level_counts = {
            "clean": sum(1 for result in results if result["risk_level"] == "clean"),
            "medium": sum(1 for result in results if result["risk_level"] == "medium"),
            "high": sum(1 for result in results if result["risk_level"] == "high"),
        }
        _print_title(out, "QC 合规关键词扫描")
        for index, result in enumerate(results, start=1):
            print(f"{index}. risk_level：{result['risk_level']}，violation_count：{result['violation_count']}", file=out)
        print("", file=out)
        print(f"- 总条数：{len(results)}", file=out)
        print(f"- clean：{level_counts['clean']}", file=out)
        print(f"- medium：{level_counts['medium']}", file=out)
        print(f"- high：{level_counts['high']}", file=out)
        print("PASS qc-scan", file=out)


def _handle_script(args: argparse.Namespace, out: TextIO) -> None:
    try:
        context = load_case_context(args.case_id)
        frequency_check = check_frequency(context["case_id"], args.channel, context)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        raise CliInputError(exc) from exc

    if not frequency_check["allowed"]:
        print(f"BLOCKED: {frequency_check['block_reason']}", file=out)
        return

    api_key = os.getenv("DEEPSEEK_API_KEY") if args.use_llm else None
    if args.use_llm and not api_key:
        print("LLM polish skipped: DEEPSEEK_API_KEY not found", file=out)

    try:
        draft = generate_script_draft(context["case_id"], args.channel, context, api_key=api_key)
    except Exception as exc:  # noqa: BLE001
        if api_key:
            print(f"LLM polish failed ({exc})，falling back to deterministic draft", file=out)
            draft = generate_script_draft(context["case_id"], args.channel, context, api_key=None)
        else:
            raise CliInputError(exc) from exc

    scan = draft["compliance_scan"]
    freq = draft["frequency_check"]
    scan_label = "CLEAN" if scan["risk_level"] == "clean" else scan["risk_level"].upper()
    check_mark = "✓" if freq["allowed"] else "x"

    print("=== 话术草稿 ===", file=out)
    print(
        "案件: {} | 渠道: {} | 类型: {}".format(
            draft["case_id"],
            _display_channel(draft["channel"]),
            draft["script_type"],
        ),
        file=out,
    )
    print("---", file=out)
    print(draft["draft_content"], file=out)
    print("---", file=out)
    print(f"合规扫描: {scan_label}（{scan['violation_count']}个违规）", file=out)
    print(
        "频次检查: 今日{}次/上限{}次，本周{}次/上限{}次 {}".format(
            freq["today_count"],
            freq["daily_limit"],
            freq["week_count"],
            freq["weekly_limit"],
            check_mark,
        ),
        file=out,
    )
    print(f"风险等级: {draft['risk_level']}", file=out)
    print(f"主管复核: {'需要' if draft['supervisor_review_required'] else '不需要'}", file=out)
    print("---", file=out)
    if args.approve:
        approve_and_log(draft)
        print("Mock 发送已写入日志", file=out)
    else:
        print("等待人工确认，使用 --approve 确认发送", file=out)


def _handle_render_model_lab(args: argparse.Namespace, out: TextIO) -> None:
    scenarios = _load_scenarios(args.scenarios)
    errors = validate_strategy_scenarios(scenarios)
    if errors:
        raise CliInputError(f"strategy scenario validation failed: {errors}")

    try:
        strategy_eval = run_strategy_evaluation(
            scenarios_path=args.scenarios,
            m3_summary_path=args.m3_summary,
            output_json=args.strategy_eval_json,
            output_md=args.strategy_eval_md,
        )
        roi = calculate_roi_results(load_strategy_eval_results(args.strategy_eval_json))
        write_roi_outputs(roi, args.roi_json, args.roi_md)
    except (FileNotFoundError, ValueError) as exc:
        raise CliInputError(exc) from exc

    print("strategy scenarios validation：PASS", file=out)
    print(f"strategy_eval_results.json：{_display_path(args.strategy_eval_json)}", file=out)
    print(f"strategy_eval_summary.md：{_display_path(args.strategy_eval_md)}", file=out)
    print(f"roi_results.json：{_display_path(args.roi_json)}", file=out)
    print(f"roi_summary.md：{_display_path(args.roi_md)}", file=out)
    print(f"scenario count：{strategy_eval['scenario_count']}", file=out)
    print(f"positive ROI scenarios：{roi['positive_roi_count']}", file=out)
    print("PASS model lab render", file=out)


def _handle_render_dashboard(args: argparse.Namespace, out: TextIO) -> None:
    try:
        context = write_dashboard(args.input, args.output)
    except DashboardInputError as exc:
        raise CliInputError(exc) from exc
    overview = _as_dict(context.get("overview"))
    print("dashboard html：{}".format(_display_path(args.output)), file=out)
    print("input：{}".format(_display_path(args.input)), file=out)
    print("anomalies：{}".format(_safe_int(overview.get("anomaly_count"))), file=out)
    print("top drivers：{}".format(len(_as_list(context.get("top_drivers")))), file=out)


def _handle_render_report(args: argparse.Namespace, out: TextIO) -> None:
    try:
        context = write_business_report(args.input, args.output, args.html_output)
    except BusinessReportInputError as exc:
        raise CliInputError(exc) from exc
    overview = _as_dict(context.get("overview"))
    print("business report markdown：{}".format(_display_path(args.output)), file=out)
    print("business report html：{}".format(_display_path(args.html_output)), file=out)
    print("input：{}".format(_display_path(args.input)), file=out)
    print("anomalies：{}".format(_safe_int(overview.get("anomaly_count"))), file=out)
    print("top drivers：{}".format(len(_as_list(context.get("top_drivers")))), file=out)


def _handle_render_excel(args: argparse.Namespace, out: TextIO) -> None:
    try:
        result = write_business_report_excel(args.input, args.output, args.roi_input)
    except BusinessReportInputError as exc:
        raise CliInputError(exc) from exc
    print("business report excel：{}".format(_display_path(args.output)), file=out)
    print("input：{}".format(_display_path(args.input)), file=out)
    print("roi input：{}".format(_display_path(args.roi_input)), file=out)
    print("anomalies：{}".format(_safe_int(result.get("anomaly_count"))), file=out)


def _handle_render_ppt(args: argparse.Namespace, out: TextIO) -> None:
    try:
        result = write_business_report_ppt(args.input, args.output, args.roi_input)
    except BusinessReportInputError as exc:
        raise CliInputError(exc) from exc
    print("business report ppt：{}".format(_display_path(args.output)), file=out)
    print("input：{}".format(_display_path(args.input)), file=out)
    print("roi input：{}".format(_display_path(args.roi_input)), file=out)
    print("slides：{}".format(_safe_int(result.get("slide_count"))), file=out)


def _handle_render_charts(args: argparse.Namespace, out: TextIO) -> None:
    m3_summary = _load_summary(args.m3_summary)
    roi_results = _load_json_object(args.roi, "ROI results")
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = [
        (output_dir / "anomaly_severity.html", build_anomaly_severity_chart(m3_summary)),
        (output_dir / "driver_contribution.html", build_driver_contribution_chart(m3_summary)),
        (output_dir / "roi_comparison.html", build_roi_comparison_chart(roi_results)),
        (output_dir / "collection_funnel.html", build_collection_funnel_chart()),
        (output_dir / "waterfall.html", build_waterfall_chart()),
        (output_dir / "vendor_matrix.html", build_vendor_matrix_chart()),
        (output_dir / "capacity_heatmap.html", build_capacity_heatmap_chart()),
        (output_dir / "dpd_structure.html", build_dpd_structure_chart()),
        (output_dir / "reduction_roi.html", build_reduction_roi_chart()),
        (output_dir / "complaint_risk.html", build_complaint_risk_chart()),
    ]
    for path, html in outputs:
        path.write_text(html, encoding="utf-8")
        print(_display_path(path), file=out)
    print("PASS render-charts", file=out)


def _load_summary(input_path: Path) -> dict[str, Any]:
    if not input_path.exists():
        raise CliInputError(
            f"M3 summary 输入文件不存在：{input_path}。请先生成 outputs/m3/m3_summary.json。"
        )
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliInputError(f"M3 summary 输入文件不是合法 JSON：{input_path}。错误：{exc}") from exc
    if not isinstance(payload, dict):
        raise CliInputError(f"M3 summary 输入文件结构不符合预期：{input_path} 顶层必须是 JSON object。")
    return payload


def _load_scenarios(config_path: Path) -> list[dict[str, Any]]:
    try:
        scenarios = load_strategy_scenarios(config_path)
    except (FileNotFoundError, ValueError) as exc:
        raise CliInputError(exc) from exc
    errors = validate_strategy_scenarios(scenarios)
    if errors:
        raise CliInputError(f"strategy scenario validation failed: {errors}")
    return scenarios


def _load_json_object(input_path: Path, label: str) -> dict[str, Any]:
    if not input_path.exists():
        raise CliInputError(f"{label} 输入文件不存在：{input_path}。请先运行 render-model-lab。")
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliInputError(f"{label} 输入文件不是合法 JSON：{input_path}。错误：{exc}") from exc
    if not isinstance(payload, dict):
        raise CliInputError(f"{label} 输入文件结构不符合预期：{input_path} 顶层必须是 JSON object。")
    return payload


def _print_title(out: TextIO, title: str) -> None:
    print(title, file=out)
    print("=" * len(title), file=out)


def _print_common_commands(out: TextIO) -> None:
    print("常用命令入口：", file=out)
    for command in COMMON_COMMANDS:
        print(f"- {command}", file=out)


def _driver_role_and_type(driver: dict[str, Any]) -> tuple[str, str]:
    dimension_name = str(driver.get("dimension_name") or "")
    dimension_value = str(driver.get("dimension_value") or "")
    if dimension_name == "channel_code":
        return "渠道结构线索", "attribution signal"
    if dimension_name == "province":
        return "区域切片线索", "attribution signal"
    if dimension_name == "score_band":
        return "客群风险分层线索", "attribution signal"
    if dimension_name == "line_id":
        return "催收作业线 / 分案作业队列", "capacity / operation signal"
    if dimension_name == "region" and dimension_value == "华东":
        return "产能压力线索", "capacity pressure signal"
    return "归因线索", "attribution signal"


def _format_metric_value(item: dict[str, Any], *, key: str = "baseline_value") -> str:
    value = item.get(key)
    metric_code = str(item.get("metric_code") or "")
    if metric_code == "avg_case_per_collector":
        return _format_number(value)
    if metric_code == "complaint_per_10k_cases":
        return _format_number(value)
    if metric_code.endswith("_rate") or metric_code.endswith("_share") or metric_code.endswith("_coverage"):
        return _format_pct(value)
    return _format_pct(value) if _looks_like_ratio(value) else _format_number(value)


def _format_pct(value: Any, *, signed: bool = False) -> str:
    if not isinstance(value, int | float):
        return "-"
    pct = value * 100
    prefix = "+" if signed and pct > 0 else ""
    return f"{prefix}{pct:.2f}%"


def _format_number(value: Any) -> str:
    if not isinstance(value, int | float):
        return "-"
    return f"{value:.2f}"


def _format_money(value: Any) -> str:
    if not isinstance(value, int | float):
        return "-"
    return f"{value:,.2f}"


def _format_boundary(value: Any) -> str:
    boundaries = [str(item) for item in _as_list(value)]
    return ", ".join(boundaries) if boundaries else "-"


def _looks_like_ratio(value: Any) -> bool:
    return isinstance(value, int | float) and -1 <= value <= 1


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _display_channel(channel: str) -> str:
    return {"sms": "SMS", "ai_call": "AI外呼", "manual": "人工电话"}.get(channel, channel)


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
