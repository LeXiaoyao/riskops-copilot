from __future__ import annotations

import json
from pathlib import Path

from riskops.engines.report.feishu_md_renderer import FEISHU_FOOTER, _to_feishu_markdown, render_feishu_markdown
from tests.test_business_report import sample_summary

ROOT = Path(__file__).resolve().parents[1]


def test_render_feishu_markdown_creates_weekly_report_variant() -> None:
    output_path = ROOT / "outputs" / "reports" / "weekly_report.feishu.md"

    result = render_feishu_markdown(sample_summary(), output_path)

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert result["format"] == "feishu_markdown"
    assert "file://" not in content
    assert ROOT.as_posix() not in content
    assert FEISHU_FOOTER in content
    assert "~~" not in content
    assert "| 项目 | 内容 |" in content
    assert "| --- | --- |" in content


def test_feishu_markdown_sanitizes_gfm_strikethrough_and_image_paths(tmp_path: Path) -> None:
    output_path = tmp_path / "outputs" / "reports" / "weekly_report.feishu.md"
    image_path = tmp_path / "outputs" / "visualization" / "driver.png"
    markdown = f"# Title\n\n~~重点~~ `metric_code` 😀\n\n![driver](file://{image_path})\n"

    content = _to_feishu_markdown(markdown, {"overview": {}, "target": {}, "top_drivers": []}, output_path)

    assert "~~" not in content
    assert "~重点~" in content
    assert "`metric_code`" in content
    assert "😀" in content
    assert "file://" not in content
    assert image_path.as_posix() not in content
    assert "![driver](../visualization/driver.png)" in content


def test_write_business_report_can_emit_feishu_variant(tmp_path: Path) -> None:
    from riskops.engines.report import write_business_report

    input_path = tmp_path / "m3_summary.json"
    output_md = tmp_path / "m4_business_report.md"
    output_html = tmp_path / "m4_business_report.html"
    output_feishu = tmp_path / "weekly_report.feishu.md"
    input_path.write_text(json.dumps(sample_summary(), ensure_ascii=False), encoding="utf-8")

    write_business_report(input_path, output_md, output_html, output_feishu)

    assert output_md.exists()
    assert output_html.exists()
    assert output_feishu.exists()
    assert FEISHU_FOOTER in output_feishu.read_text(encoding="utf-8")
