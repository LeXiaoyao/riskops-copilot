"""Report writer agent for M4 business report outputs."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from riskops.engines.report import BusinessReportInputError, write_business_report, write_business_report_excel, write_business_report_word

try:
    from riskops.engines.report.ppt_renderer import render_ppt
except ImportError:
    from riskops.engines.report.ppt_renderer import write_business_report_ppt as render_ppt

ROOT = Path(__file__).resolve().parents[2]
M3_SUMMARY = ROOT / "outputs" / "m3" / "m3_summary.json"
ROI_RESULTS = ROOT / "outputs" / "model_lab" / "roi_results.json"
REPORT_DIR = ROOT / "outputs" / "reports"

FALLBACK_SYSTEM = """你是 RiskOps 报告生成专家。根据用户需求选择报告格式（MD/HTML/Excel/PPT）并调用对应引擎。
报告结构遵循：先结论后数据，每节一句话结论，数据可追溯。"""


class ReportWriterAgent:
    display_name = "报告生成专家"
    TOOLS: list[dict] = []

    def __init__(self, api_key: str | None, model: str = "deepseek-chat") -> None:
        self.api_key = api_key
        self.model = model
        self.system_prompt = _read_prompt("report_writer.txt", FALLBACK_SYSTEM)

    def run(self, message: str) -> Iterator[str]:
        if not self.api_key:
            yield "未设置 DEEPSEEK_API_KEY，报告生成将直接使用本地报告引擎。\n\n"

        msg = message.lower()
        try:
            if "excel" in msg:
                output = REPORT_DIR / "m4_business_report.xlsx"
                yield "正在生成 Excel 报告...\n"
                write_business_report_excel(M3_SUMMARY, output, ROI_RESULTS)
                yield f"Excel 报告已生成：{_display_path(output)}\n"
            elif "ppt" in msg:
                output = REPORT_DIR / "m4_business_report.pptx"
                yield "正在生成 PPT...\n"
                render_ppt(M3_SUMMARY, output, ROI_RESULTS)
                yield f"PPT 已生成：{_display_path(output)}\n"
            elif any(k in msg for k in ["word", "docx", "word草稿", "word报告"]):
                output = REPORT_DIR / "m4_business_report.docx"
                yield "正在生成 Word 草稿...\n"
                write_business_report_word(M3_SUMMARY, output, ROI_RESULTS)
                yield f"Word 草稿已生成：{_display_path(output)}\n"
            else:
                output_md = REPORT_DIR / "m4_business_report.md"
                output_html = REPORT_DIR / "m4_business_report.html"
                yield "正在生成 Markdown/HTML 报告...\n"
                write_business_report(M3_SUMMARY, output_md, output_html)
                yield f"报告已生成：{_display_path(output_md)}\n"
                yield f"HTML 报告已生成：{_display_path(output_html)}\n"
        except BusinessReportInputError as exc:
            yield f"报告生成失败：{exc}\n"


def _read_prompt(filename: str, fallback: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / filename
    if not path.exists():
        return fallback
    content = path.read_text(encoding="utf-8").strip()
    return content or fallback


def _display_path(path: Path) -> str:
    return str(path.relative_to(ROOT))
