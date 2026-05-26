"""Compliance QA agent for collection script scans."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from riskops.engines.qc import generate_qc_report, scan_batch, scan_text

FALLBACK_SYSTEM = """你是 RiskOps 合规质检专家，专注于催收话术的合规性评估。
对每条输入话术输出：合规评分(0-100)、违规类别、违规词位置、改进建议。
红线词命中时合规评分强制 ≤ 30。"""


class ComplianceQAAgent:
    display_name = "合规质检专家"
    TOOLS: list[dict] = []

    def __init__(self, api_key: str | None, model: str = "deepseek-chat") -> None:
        self.api_key = api_key
        self.model = model
        self.system_prompt = _read_prompt("compliance_qa.txt", FALLBACK_SYSTEM)

    def run(self, message: str) -> Iterator[str]:
        if not self.api_key:
            yield "未设置 DEEPSEEK_API_KEY，将使用本地合规规则扫描。\n\n"

        text = _extract_quoted_text(message)
        if not text:
            yield "请提供需要质检的话术文本，并用引号括起来，例如：质检“请尽快联系我们协商还款”。\n"
            return

        result = scan_text(text)
        score = _score(result)
        yield "### 合规质检结果\n"
        yield f"- 合规评分：{score}/100\n"
        yield f"- 风险等级：{result.get('risk_level', 'unknown')}\n"
        yield f"- 违规命中数：{result.get('violation_count', 0)}\n"
        yield f"- 摘要：{result.get('summary', '')}\n"
        yield "\n### 11维评分\n"
        for category, category_score in _dimension_scores(result).items():
            yield f"- {category}：{category_score}/100\n"
        violations = result.get("violations", [])
        if violations:
            yield "\n### 违规位置\n"
            for item in violations:
                yield f"- 类别：{item.get('category')}；关键词：{item.get('keyword')}；位置：{item.get('position')}\n"
        yield "\n### 改进建议\n"
        if violations:
            yield "- 删除红线词，改为协商、提醒和官方渠道表达；发送前必须人工复核。\n"
        else:
            yield "- 未发现本地规则命中的红线词，仍需人工复核语境和触达频次。\n"


def _extract_quoted_text(message: str) -> str | None:
    patterns = [
        r"“([^”]+)”",
        r"\"([^\"]+)\"",
        r"‘([^’]+)’",
        r"'([^']+)'",
    ]
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip()
    return None


def _score(result: dict) -> int:
    violation_count = int(result.get("violation_count", 0) or 0)
    if violation_count == 0:
        return 100
    if result.get("risk_level") == "high":
        return 30
    return max(60, 90 - violation_count * 15)


def _dimension_scores(result: dict) -> dict[str, int]:
    dimensions = {
        "威胁恐吓": 100,
        "冒充司法": 100,
        "骚扰第三方": 100,
        "诱导新贷": 100,
        "辱骂侮辱": 100,
        "隐私保护": 100,
        "频次边界": 100,
        "身份表述": 100,
        "协商导向": 100,
        "时段合规": 100,
        "人工复核": 100,
    }
    for item in result.get("violations", []):
        category = item.get("category")
        if category in dimensions:
            dimensions[category] = min(dimensions[category], 30)
    return dimensions


def _read_prompt(filename: str, fallback: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / filename
    if not path.exists():
        return fallback
    content = path.read_text(encoding="utf-8").strip()
    return content or fallback


__all__ = ["ComplianceQAAgent", "generate_qc_report", "scan_batch", "scan_text"]
