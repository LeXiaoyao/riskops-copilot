"""Lightweight CLI interaction MVP for M5."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO

from riskops.engines.dashboard import DashboardInputError, write_dashboard
from riskops.engines.report import BusinessReportInputError, write_business_report

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_M3_SUMMARY = ROOT / "outputs" / "m3" / "m3_summary.json"
DEFAULT_DASHBOARD = ROOT / "outputs" / "dashboard" / "dashboard.html"
DEFAULT_REPORT_MD = ROOT / "outputs" / "reports" / "m4_business_report.md"
DEFAULT_REPORT_HTML = ROOT / "outputs" / "reports" / "m4_business_report.html"

OUTPUT_PATHS = [
    DEFAULT_DASHBOARD,
    DEFAULT_REPORT_MD,
    DEFAULT_REPORT_HTML,
    ROOT / "outputs" / "m3" / "m3_summary.md",
    DEFAULT_M3_SUMMARY,
]

COMMON_COMMANDS = [
    "python scripts/riskops_cli.py summary",
    "python scripts/riskops_cli.py anomalies",
    "python scripts/riskops_cli.py drivers",
    "python scripts/riskops_cli.py outputs",
    "python scripts/riskops_cli.py render-dashboard",
    "python scripts/riskops_cli.py render-report",
]


class CliInputError(RuntimeError):
    """Raised when CLI input files are missing or malformed."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RiskOps Copilot M5 CLI interaction MVP.",
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
    print("- 当前阶段：M5 TUI / CLI Interaction MVP", file=out)
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


def _looks_like_ratio(value: Any) -> bool:
    return isinstance(value, int | float) and -1 <= value <= 1


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


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
