"""Load generated RiskOps outputs for TUI chat context."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_CONTEXT_CHARS = 8000
MISSING_DATA_MESSAGE = "该数据未生成，请先运行 bash scripts/run_all.sh"

CONTEXT_FILES: tuple[tuple[str, Path], ...] = (
    ("M3 异常报告", ROOT / "outputs" / "m3" / "m3_summary.md"),
    ("异常检测结果", ROOT / "outputs" / "anomalies" / "anomaly_results.md"),
    ("归因摘要", ROOT / "outputs" / "attribution" / "attribution_summary.md"),
    ("策略 ROI", ROOT / "outputs" / "model_lab" / "roi_summary.md"),
    ("Copilot Briefing", ROOT / "outputs" / "copilot" / "briefing.md"),
)


def load_context() -> str:
    sections: list[str] = []
    for title, path in CONTEXT_FILES:
        if path.exists():
            content = path.read_text(encoding="utf-8")
        else:
            content = MISSING_DATA_MESSAGE
        sections.append(f"## {title}\n来源：{_display_path(path)}\n\n{content.strip()}")

    context = "\n\n---\n\n".join(sections)
    if len(context) <= MAX_CONTEXT_CHARS:
        return context
    return context[:MAX_CONTEXT_CHARS] + "\n\n[上下文已截断到 8000 字符]"


def context_summary() -> str:
    lines = ["当前加载的数据摘要："]
    total_chars = 0
    existing_count = 0
    for title, path in CONTEXT_FILES:
        if path.exists():
            char_count = len(path.read_text(encoding="utf-8"))
            existing_count += 1
            total_chars += char_count
            status = f"已加载，{char_count} 字符"
        else:
            status = "未生成"
        lines.append(f"- {title}：{status}")
    lines.append(f"- 合计：{existing_count} 个文件，{total_chars} 字符，LLM 上下文最多 8000 字符")
    return "\n".join(lines)


def read_output(name: str) -> str:
    lookup = {
        "summary": CONTEXT_FILES[0],
        "anomaly": CONTEXT_FILES[1],
        "drivers": CONTEXT_FILES[2],
        "roi": CONTEXT_FILES[3],
        "briefing": CONTEXT_FILES[4],
    }
    title, path = lookup[name]
    if not path.exists():
        return MISSING_DATA_MESSAGE
    return f"## {title}\n\n{path.read_text(encoding='utf-8').strip()}"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)
