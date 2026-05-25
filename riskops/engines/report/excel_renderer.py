"""Excel renderer for the M4 business report."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from riskops.engines.report.business_report import BusinessReportInputError, load_m3_summary

HEADER_FILL = "1F4E79"
HEADER_FONT = "FFFFFF"


class ExcelReportInputError(BusinessReportInputError):
    """Raised when Excel report inputs are missing or malformed."""


def write_business_report_excel(
    m3_summary_path: Path,
    output_path: Path,
    roi_results_path: Path,
) -> dict[str, Any]:
    summary = load_m3_summary(m3_summary_path)
    roi_results = load_roi_results(roi_results_path)

    workbook = Workbook()
    overview = workbook.active
    overview.title = "概览"

    _write_overview_sheet(overview, summary)
    _write_table(
        workbook.create_sheet("异常信号"),
        ["metric_code", "metric_name_cn", "current_value", "baseline_value", "relative_change", "severity"],
        _anomaly_rows(summary),
    )
    _write_table(
        workbook.create_sheet("归因 Top5"),
        ["dimension_name", "dimension_value", "contribution_score", "recommended_action"],
        _driver_rows(summary),
    )
    _write_table(
        workbook.create_sheet("策略ROI"),
        ["scenario_id", "roi_ratio", "estimated_cost", "estimated_benefit", "payback_months"],
        _roi_rows(roi_results),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return {"output_path": str(output_path), "anomaly_count": len(_anomaly_rows(summary))}


def load_roi_results(input_path: Path) -> dict[str, Any]:
    if not input_path.exists():
        raise ExcelReportInputError(f"ROI 输入文件不存在：{input_path}。请先运行 render-model-lab。")
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ExcelReportInputError(f"ROI 输入文件不是合法 JSON：{input_path}。错误：{exc}") from exc
    if not isinstance(payload, dict):
        raise ExcelReportInputError(f"ROI 输入文件结构不符合预期：{input_path} 顶层必须是 JSON object。")
    return payload


def _write_overview_sheet(sheet: Worksheet, summary: dict[str, Any]) -> None:
    overview = _as_dict(summary.get("anomaly_overview"))
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))
    target = _as_dict(attribution.get("target_anomaly")) or _as_dict(summary.get("attribution_target_anomaly"))
    target_metric_code = attribution.get("target_metric_code") or target.get("metric_code")
    target_metric_name = attribution.get("target_metric_name_cn") or target.get("metric_name_cn")

    rows = [
        ("anomaly_count", overview.get("anomaly_count")),
        ("severity_counts", _format_severity_counts(_as_dict(overview.get("severity_counts")))),
        ("target_metric", _format_target_metric(target_metric_code, target_metric_name)),
        ("relative_change", target.get("relative_change")),
        ("生成时间", datetime.now(UTC).replace(microsecond=0).isoformat()),
    ]
    _write_table(sheet, ["field", "value"], rows)


def _write_table(sheet: Worksheet, headers: list[str], rows: list[tuple[Any, ...]]) -> None:
    sheet.append(headers)
    _style_header(sheet)
    for row in rows:
        sheet.append(list(row))
    sheet.freeze_panes = "A2"
    _autosize_columns(sheet)


def _style_header(sheet: Worksheet) -> None:
    fill = PatternFill("solid", fgColor=HEADER_FILL)
    font = Font(bold=True, color=HEADER_FONT)
    for cell in sheet[1]:
        cell.fill = fill
        cell.font = font


def _autosize_columns(sheet: Worksheet) -> None:
    for column_cells in sheet.columns:
        width = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            width = max(width, len(str(cell.value)) if cell.value is not None else 0)
        sheet.column_dimensions[column_letter].width = min(max(width + 2, 12), 48)


def _anomaly_rows(summary: dict[str, Any]) -> list[tuple[Any, ...]]:
    anomalies = [item for item in _as_list(summary.get("high_priority_anomalies")) if isinstance(item, dict)]
    return [
        (
            anomaly.get("metric_code"),
            anomaly.get("metric_name_cn"),
            anomaly.get("recent_value"),
            anomaly.get("baseline_value"),
            anomaly.get("relative_change"),
            anomaly.get("severity"),
        )
        for anomaly in anomalies
    ]


def _driver_rows(summary: dict[str, Any]) -> list[tuple[Any, ...]]:
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))
    drivers = [item for item in _as_list(attribution.get("top_drivers")) if isinstance(item, dict)][:5]
    return [
        (
            driver.get("dimension_name"),
            driver.get("dimension_value"),
            driver.get("contribution_score"),
            driver.get("recommended_action"),
        )
        for driver in drivers
    ]


def _roi_rows(roi_results: dict[str, Any]) -> list[tuple[Any, ...]]:
    results = [item for item in _as_list(roi_results.get("results")) if isinstance(item, dict)]
    return [
        (
            result.get("scenario_id"),
            result.get("roi_ratio"),
            result.get("action_cost"),
            result.get("gross_benefit"),
            _payback_months(result.get("payback_period_days")),
        )
        for result in results
    ]


def _payback_months(value: Any) -> float | None:
    if not isinstance(value, int | float):
        return None
    return round(value / 30, 4)


def _format_severity_counts(severity_counts: dict[str, Any]) -> str:
    return ", ".join(f"{key}={severity_counts.get(key, 0)}" for key in ("high", "medium", "low"))


def _format_target_metric(metric_code: Any, metric_name: Any) -> str:
    if metric_code and metric_name:
        return f"{metric_name} ({metric_code})"
    return str(metric_name or metric_code or "")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
