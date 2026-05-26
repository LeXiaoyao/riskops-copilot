"""Demo compliance keyword scanner for collection scripts."""

from __future__ import annotations

import unicodedata
from pathlib import Path

VIOLATION_DICT = {
    "威胁恐吓": ["起诉你", "拘留", "坐牢", "警察上门", "法院传票", "强制执行"],
    "冒充司法": ["我是法院", "我是公安", "司法拍卖", "检察院"],
    "骚扰第三方": ["联系你家人", "找你家人", "告诉你同事", "找你单位", "联系你亲属", "找你亲属", "联系你父母", "找你朋友"],
    "诱导新贷": ["借新还旧", "先贷款还款", "再借一笔"],
    "辱骂侮辱": ["骗子", "老赖", "无耻", "不要脸", "废物"],
}


def scan_text(text: str) -> dict:
    """Scan one text item and return a deterministic compliance risk report."""

    normalized_text, position_map = _normalize_with_position_map(text)
    violations = []

    for category, keywords in VIOLATION_DICT.items():
        for keyword in keywords:
            normalized_keyword = unicodedata.normalize("NFKC", keyword)
            start = normalized_text.find(normalized_keyword)
            while start != -1:
                violations.append(
                    {
                        "category": category,
                        "keyword": keyword,
                        "position": position_map[start] if start < len(position_map) else start,
                    }
                )
                start = normalized_text.find(normalized_keyword, start + len(normalized_keyword))

    violations.sort(key=lambda item: (item["position"], item["category"], item["keyword"]))
    violation_count = len(violations)
    risk_level = _risk_level(violation_count)
    return {
        "text_length": len(text),
        "violation_count": violation_count,
        "violations": violations,
        "risk_level": risk_level,
        "summary": _summary(violation_count, risk_level),
    }


def scan_batch(texts: list[str]) -> list[dict]:
    """Scan multiple text items."""

    return [scan_text(text) for text in texts]


def generate_qc_report(results: list[dict], output_path: str | Path) -> str:
    """Write a Markdown report and return the output path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    clean_count = sum(1 for result in results if result.get("risk_level") == "clean")
    medium_count = sum(1 for result in results if result.get("risk_level") == "medium")
    high_count = sum(1 for result in results if result.get("risk_level") == "high")

    lines = [
        "## QC 合规扫描报告",
        "",
        f"- 总条数：{len(results)}",
        f"- clean 数：{clean_count}",
        f"- medium 数：{medium_count}",
        f"- high 数：{high_count}",
        "",
        "## 违规详情（仅 high 风险）",
        "",
    ]

    high_results = [(index, result) for index, result in enumerate(results, start=1) if result.get("risk_level") == "high"]
    if not high_results:
        lines.append("- 无 high 风险话术。")
    for index, result in high_results:
        lines.append(f"### 第 {index} 条")
        for violation in result.get("violations", []):
            lines.append(f"- 类别：{violation['category']}")
            lines.append(f"  关键词：{violation['keyword']}")
            lines.append(f"  位置：{violation['position']}")
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return str(path)


def scan_text_with_llm(text: str, api_key: str, model: str = "deepseek-chat") -> dict:
    """Keyword scan + LLM 11-dimension scoring merged with red-line override.

    Returns the merged result dict (see llm_scorer.merge_with_keyword_scan).
    Falls back gracefully when DeepSeek is unavailable.
    """
    from riskops.engines.qc.llm_scorer import merge_with_keyword_scan, score_with_llm  # noqa: PLC0415

    keyword_result = scan_text(text)
    llm_result = score_with_llm(text, api_key, model)
    return merge_with_keyword_scan(llm_result, keyword_result)


def _normalize_with_position_map(text: str) -> tuple[str, list[int]]:
    normalized_chars = []
    position_map = []
    for index, char in enumerate(text):
        normalized = unicodedata.normalize("NFKC", char)
        normalized_chars.append(normalized)
        position_map.extend([index] * len(normalized))
    return "".join(normalized_chars), position_map


def _risk_level(violation_count: int) -> str:
    if violation_count == 0:
        return "clean"
    if violation_count <= 2:
        return "medium"
    return "high"


def _summary(violation_count: int, risk_level: str) -> str:
    if violation_count == 0:
        return "未发现违规关键词，风险等级 clean。"
    return f"发现 {violation_count} 个违规关键词，风险等级 {risk_level}。"
