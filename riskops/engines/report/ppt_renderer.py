"""PowerPoint renderer for the M4 business report."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from riskops.engines.report.business_report import BusinessReportInputError, load_m3_summary
from riskops.engines.report.excel_renderer import load_roi_results

TITLE_BAR_COLOR = RGBColor(0x1F, 0x4E, 0x79)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BODY_COLOR = RGBColor(0x1F, 0x1F, 0x1F)
TITLE_FONT_SIZE = Pt(18)
BODY_FONT_SIZE = Pt(14)


class PptReportInputError(BusinessReportInputError):
    """Raised when PPT report inputs are missing or malformed."""


def write_business_report_ppt(
    m3_summary_path: Path,
    output_path: Path,
    roi_results_path: Path,
) -> dict[str, Any]:
    summary = load_m3_summary(m3_summary_path)
    try:
        roi_results = load_roi_results(roi_results_path)
    except BusinessReportInputError as exc:
        raise PptReportInputError(str(exc)) from exc

    presentation = Presentation()
    _add_title_slide(presentation)
    _add_core_conclusion_slide(presentation, summary)
    _add_anomaly_slide(presentation, summary)
    _add_attribution_slide(presentation, summary)
    _add_roi_slide(presentation, roi_results)
    _add_boundary_slide(presentation)
    _add_next_actions_slide(presentation)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    presentation.save(output_path)
    return {"output_path": str(output_path), "slide_count": len(presentation.slides)}


def _add_title_slide(presentation: Presentation) -> None:
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    _add_header(slide, "RiskOps Copilot")
    textbox = slide.shapes.add_textbox(Inches(0.9), Inches(1.7), Inches(8.2), Inches(2.6))
    frame = textbox.text_frame
    frame.clear()

    _add_paragraph(frame, "RiskOps Copilot", bold=True)
    _add_paragraph(frame, "贷后经营复盘", bold=True)
    _add_paragraph(frame, f"生成时间：{_generated_at_text()}")


def _add_core_conclusion_slide(presentation: Presentation, summary: dict[str, Any]) -> None:
    overview = _as_dict(summary.get("anomaly_overview"))
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))
    target = _as_dict(attribution.get("target_anomaly")) or _as_dict(summary.get("attribution_target_anomaly"))
    severity_counts = _as_dict(overview.get("severity_counts"))

    lines = [
        f"M1 D7 回收率变动幅度：{_format_pct(target.get('relative_change'), signed=True)}",
        f"异常数量：{_safe_int(overview.get('anomaly_count'))}",
        "严重度分布：high={} / medium={} / low={}".format(
            _safe_int(severity_counts.get("high")),
            _safe_int(severity_counts.get("medium")),
            _safe_int(severity_counts.get("low")),
        ),
        "结论边界：该结果来自 synthetic data，仅用于 demo 复盘。",
    ]
    slide = _add_content_slide(presentation, "核心结论")
    _add_bullets(slide, lines)


def _add_anomaly_slide(presentation: Presentation, summary: dict[str, Any]) -> None:
    anomalies = [item for item in _as_list(summary.get("high_priority_anomalies")) if isinstance(item, dict)]
    lines = [
        "{} / {} / {}".format(
            anomaly.get("metric_name_cn") or "-",
            anomaly.get("severity") or "-",
            _format_pct(anomaly.get("relative_change"), signed=True),
        )
        for anomaly in anomalies
    ]
    slide = _add_content_slide(presentation, "异常信号")
    _add_bullets(slide, lines or ["未发现异常信号。"])


def _add_attribution_slide(presentation: Presentation, summary: dict[str, Any]) -> None:
    attribution = _as_dict(summary.get("m1_d7_attribution_summary"))
    drivers = [item for item in _as_list(attribution.get("top_drivers")) if isinstance(item, dict)][:5]
    lines = [
        "{}：{}={}，贡献度 {}".format(
            _driver_category(driver.get("dimension_name")),
            driver.get("dimension_name") or "-",
            driver.get("dimension_value") or "-",
            _format_pct(driver.get("contribution_score")),
        )
        for driver in drivers
    ]
    slide = _add_content_slide(presentation, "归因 Top5")
    _add_bullets(slide, lines or ["未发现归因因子。"])


def _add_roi_slide(presentation: Presentation, roi_results: dict[str, Any]) -> None:
    rows = [item for item in _as_list(roi_results.get("results")) if isinstance(item, dict)][:5]
    slide = _add_content_slide(presentation, "策略 ROI 对比")
    if not rows:
        _add_bullets(slide, ["未发现 ROI 情景。"])
        return

    table_shape = slide.shapes.add_table(
        rows=len(rows) + 1,
        cols=3,
        left=Inches(0.7),
        top=Inches(1.25),
        width=Inches(8.9),
        height=Inches(3.8),
    )
    table = table_shape.table
    headers = ["情景", "ROI ratio", "payback"]
    for col, header in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = header
        _style_cell(cell, bold=True, fill=TITLE_BAR_COLOR, color=WHITE)
    for row_index, result in enumerate(rows, start=1):
        values = [
            str(result.get("scenario_name") or result.get("scenario_id") or "-"),
            _format_number(result.get("roi_ratio")),
            _format_payback(result.get("payback_period_days")),
        ]
        for col, value in enumerate(values):
            cell = table.cell(row_index, col)
            cell.text = value
            _style_cell(cell)


def _add_boundary_slide(presentation: Presentation) -> None:
    slide = _add_content_slide(presentation, "AI+ML 边界声明")
    _add_bullets(
        slide,
        [
            "synthetic data only",
            "demo boundary",
            "no real customer data",
            "no real financial conclusion",
            "no real collection action",
            "no LLM automatic decisioning",
        ],
    )


def _add_next_actions_slide(presentation: Presentation) -> None:
    slide = _add_content_slide(presentation, "Next Actions")
    _add_bullets(
        slide,
        [
            "人工复核 M1 D7 回收率口径与窗口期。",
            "下钻 Top5 归因因子的渠道、区域、客群和过程证据。",
            "复核 ROI 情景的成本假设和收益假设。",
            "确认策略动作只进入人工评审，不触发真实催收执行。",
            "补充业务 owner 结论后再进入对外材料。",
        ],
    )


def _add_content_slide(presentation: Presentation, title: str):
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    _add_header(slide, title)
    return slide


def _add_header(slide, title: str) -> None:
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.65))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TITLE_BAR_COLOR
    bar.line.color.rgb = TITLE_BAR_COLOR

    title_box = slide.shapes.add_textbox(Inches(0.45), Inches(0.11), Inches(9.1), Inches(0.42))
    frame = title_box.text_frame
    frame.clear()
    paragraph = frame.paragraphs[0]
    paragraph.alignment = PP_ALIGN.LEFT
    run = paragraph.add_run()
    run.text = title
    run.font.size = TITLE_FONT_SIZE
    run.font.bold = True
    run.font.color.rgb = WHITE


def _add_bullets(slide, lines: list[str]) -> None:
    textbox = slide.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(8.6), Inches(4.4))
    frame = textbox.text_frame
    frame.clear()
    frame.word_wrap = True
    for index, line in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = str(line)
        paragraph.level = 0
        paragraph.font.size = BODY_FONT_SIZE
        paragraph.font.color.rgb = BODY_COLOR
        paragraph.space_after = Pt(6)


def _add_paragraph(frame, text: str, *, font_size=BODY_FONT_SIZE, bold: bool = False) -> None:
    paragraph = frame.paragraphs[0] if not frame.paragraphs[0].text else frame.add_paragraph()
    paragraph.text = text
    paragraph.font.size = font_size
    paragraph.font.bold = bold
    paragraph.font.color.rgb = BODY_COLOR
    paragraph.space_after = Pt(10)


def _style_cell(cell, *, bold: bool = False, fill: RGBColor | None = None, color: RGBColor = BODY_COLOR) -> None:
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.size = BODY_FONT_SIZE
        paragraph.font.bold = bold
        paragraph.font.color.rgb = color


def _generated_at_text() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _driver_category(dimension_name: Any) -> str:
    value = str(dimension_name or "")
    if value in {"channel_code", "vendor_id", "product_code"}:
        return "渠道"
    if value in {"province", "region", "city"}:
        return "区域"
    if value in {"risk_level", "score_band", "balance_segment"}:
        return "客群"
    return "过程因子"


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


def _format_payback(value: Any) -> str:
    if not isinstance(value, int | float):
        return "-"
    if value < 1:
        return "<1 天"
    return f"{value:.1f} 天"


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
