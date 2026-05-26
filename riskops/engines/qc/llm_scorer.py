"""LLM-powered 11-dimension compliance scoring for collection scripts.

Supplements the keyword scanner with DeepSeek-based contextual evaluation.
Rule-based scanner always takes precedence on red-line violations.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# 11 维评分维度（PRD §7.5）
DIMENSIONS = [
    ("开场身份说明", "是否合规说明了身份与公司名称"),
    ("账单事实说明", "是否清楚说明了欠款事实（金额/日期/账单期）"),
    ("金额与日期说明", "是否明确说明了应还金额和截止日期"),
    ("客户异议识别", "是否识别并响应了客户可能提出的异议"),
    ("还款方案引导", "是否引导了可行的还款方案或分期减免"),
    ("情绪控制", "沟通是否克制专业，无激动/指责/施压语气"),
    ("催收强度", "催收强度是否在合理范围内（0=无压力，100=极度施压）"),
    ("合规红线", "是否触发了禁止性表达（威胁/辱骂/冒充司法/骚扰第三方等）"),
    ("投诉风险", "综合判断此话术引发客户投诉的概率"),
    ("PTP确认", "如有还款承诺引导，是否明确了金额和日期"),
    ("结束语规范", "是否以合规方式结束对话"),
]

SYSTEM_PROMPT = """你是一位资深催收合规质检专家，负责对催收话术进行专业评估。

请对输入的话术文本按以下11个维度进行评分（每维度0-100分）：
1. 开场身份说明（是否合规说明身份与公司）
2. 账单事实说明（是否清楚说明欠款事实）
3. 金额与日期说明（是否明确应还金额和截止日期）
4. 客户异议识别（是否识别并响应客户异议）
5. 还款方案引导（是否引导可行还款方案）
6. 情绪控制（沟通是否克制专业）
7. 催收强度（0=无压力，100=极度施压，合理范围30-70）
8. 合规红线（是否触发禁止性表达，无违规=100，有违规=0）
9. 投诉风险（引发投诉的概率，0=无风险，100=极高风险）
10. PTP确认（还款承诺引导是否明确金额日期，无PTP引导则给50）
11. 结束语规范（是否以合规方式结束，无结束语则给50）

同时给出：
- overall_compliance_score: 综合合规分（0-100），重点加权合规红线和情绪控制
- supervisor_review_required: true/false（合规红线<60或催收强度>80时为true）
- suggested_alternative: 如果发现问题，给出1句改进建议；无问题则为null
- risk_summary: 一句话风险概述

严格按以下JSON格式输出，不要有其他文字：
{
  "dimensions": {
    "开场身份说明": 分数,
    "账单事实说明": 分数,
    "金额与日期说明": 分数,
    "客户异议识别": 分数,
    "还款方案引导": 分数,
    "情绪控制": 分数,
    "催收强度": 分数,
    "合规红线": 分数,
    "投诉风险": 分数,
    "PTP确认": 分数,
    "结束语规范": 分数
  },
  "overall_compliance_score": 分数,
  "supervisor_review_required": true/false,
  "suggested_alternative": "改进建议或null",
  "risk_summary": "一句话风险概述"
}"""


def score_with_llm(text: str, api_key: str, model: str = "deepseek-chat") -> dict:
    """Call DeepSeek to score a collection script across 11 compliance dimensions.

    Returns a dict with dimension scores, overall score, and recommendations.
    Falls back to a rule-based estimate if the API call fails.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请对以下催收话术进行11维合规评分：\n\n{text}"},
        ],
        "temperature": 0.1,  # 低温度保证稳定的结构化输出
        "max_tokens": 600,
    }
    request = urllib.request.Request(
        DEEPSEEK_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
            # 清理 markdown 代码块
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError):
        return _fallback_score()


def merge_with_keyword_scan(llm_result: dict, keyword_result: dict) -> dict:
    """Merge LLM scores with keyword scan, enforcing red-line overrides.

    Rules:
    - If keyword scan finds red-line violations, force 合规红线 dimension ≤ 20
    - If keyword scan risk_level == "high", force overall_compliance_score ≤ 30
    - Keyword violations always appear in the final violations list
    """
    merged = dict(llm_result)

    violation_count = keyword_result.get("violation_count", 0)
    keyword_violations = keyword_result.get("violations", [])

    if violation_count > 0:
        dims = merged.get("dimensions", {})
        # 红线维度：关键词命中时强制压低
        red_line_score = max(0, 20 - violation_count * 10)
        dims["合规红线"] = min(dims.get("合规红线", 100), red_line_score)
        # 投诉风险同步上调
        dims["投诉风险"] = max(dims.get("投诉风险", 0), 60 + violation_count * 10)
        merged["dimensions"] = dims
        merged["supervisor_review_required"] = True

    if keyword_result.get("risk_level") == "high":
        merged["overall_compliance_score"] = min(
            merged.get("overall_compliance_score", 100), 30
        )
    elif keyword_result.get("risk_level") == "medium":
        merged["overall_compliance_score"] = min(
            merged.get("overall_compliance_score", 100), 65
        )

    # 追加关键词违规列表
    merged["keyword_violations"] = keyword_violations
    merged["keyword_risk_level"] = keyword_result.get("risk_level", "clean")

    return merged


def _fallback_score() -> dict:
    """Return a neutral score when LLM is unavailable."""
    return {
        "dimensions": {dim: 70 for dim, _ in DIMENSIONS},
        "overall_compliance_score": 70,
        "supervisor_review_required": False,
        "suggested_alternative": None,
        "risk_summary": "LLM 评分不可用，已退回关键词规则扫描结果。",
        "_fallback": True,
    }
