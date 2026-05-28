"""Feishu-friendly Markdown renderer for weekly business reports."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

FEISHU_FOOTER = "> 本文档由 RiskOps Copilot 自动生成，可直接粘贴到飞书文档 / 群消息。"


def render_feishu_markdown(summary: dict[str, Any], output_path: Path) -> dict[str, Any]:
    from riskops.engines.report.business_report import build_business_report_context, render_business_report_markdown

    context = build_business_report_context(summary)
    markdown = render_business_report_markdown(context)
    feishu_markdown = _to_feishu_markdown(markdown, context, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(feishu_markdown, encoding="utf-8")
    return {
        "output_path": output_path.as_posix(),
        "format": "feishu_markdown",
        "table_count": feishu_markdown.count("| --- |"),
        "footer": FEISHU_FOOTER,
    }


def _to_feishu_markdown(markdown: str, context: dict[str, Any], output_path: Path) -> str:
    content = markdown.replace("~~", "~")
    content = _relative_image_paths(content, output_path)
    content = _insert_feishu_summary_table(content, context)
    content = content.rstrip()
    if FEISHU_FOOTER not in content:
        content = f"{content}\n\n{FEISHU_FOOTER}"
    return f"{content}\n"


def _insert_feishu_summary_table(markdown: str, context: dict[str, Any]) -> str:
    overview = context.get("overview") if isinstance(context.get("overview"), dict) else {}
    target = context.get("target") if isinstance(context.get("target"), dict) else {}
    table = "\n".join(
        [
            "## 飞书协作摘要",
            "",
            "| 项目 | 内容 |",
            "| --- | --- |",
            f"| 异常总数 | {overview.get('anomaly_count', 0)} |",
            f"| high / medium / low | {_severity_text(overview.get('severity_counts'))} |",
            f"| 核心指标 | {context.get('target_metric_name_cn') or target.get('metric_name_cn') or 'N/A'} |",
            f"| Top drivers | {len(context.get('top_drivers') or [])} |",
        ]
    )
    lines = markdown.splitlines()
    if len(lines) <= 2:
        return f"{markdown.rstrip()}\n\n{table}\n"
    return "\n".join([*lines[:2], "", table, "", *lines[2:]]) + "\n"


def _severity_text(value: Any) -> str:
    counts = value if isinstance(value, dict) else {}
    return "{high} / {medium} / {low}".format(
        high=counts.get("high", 0),
        medium=counts.get("medium", 0),
        low=counts.get("low", 0),
    )


def _relative_image_paths(markdown: str, output_path: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        alt_text = match.group("alt")
        target = match.group("target").strip()
        return f"![{alt_text}]({_relative_path_target(target, output_path.parent)})"

    return re.sub(r"!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]+)\)", replace, markdown)


def _relative_path_target(target: str, output_dir: Path) -> str:
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if target.startswith("file://"):
        target = target.removeprefix("file://")
    path = Path(target)
    if not path.is_absolute():
        return path.as_posix()
    return os.path.relpath(path, start=output_dir).replace(os.sep, "/")
