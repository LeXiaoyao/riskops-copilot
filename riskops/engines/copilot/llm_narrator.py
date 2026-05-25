"""LLM narration layer for Copilot briefing.

Uses DeepSeek API (OpenAI-compatible) to generate a Chinese management
summary from the structured briefing dict. Falls back gracefully when
the API key is missing or the call fails — deterministic briefing is
always the primary output.
"""

from __future__ import annotations

import os
from typing import Any

_DEFAULT_BASE_URL = "https://api.deepseek.com"
_DEFAULT_MODEL = "deepseek-chat"

_SYSTEM_PROMPT = """你是一位消费金融贷后风险运营分析助手，帮助风险管理层快速理解当前贷后经营状态。

输出规范：
- 结论先行：第一段直接给结论，再展开数据支撑
- 数据为底：所有判断必须引用输入数据，不臆造、不夸大
- 业务语言：用"M1 D7 回收率""渠道 ECOM""供应商重配"等具体名称，避免堆砌公式
- 中文为主，技术术语（DPD、MOB、PTP、AUC、KS）保留英文
- 篇幅：4-5 段，每段 3-5 句，总字数 400-600 字
- 末段必须注明：以上基于合成数据 demo，不作为真实业务决策依据，所有策略动作需人工确认后方可执行
"""

_USER_PROMPT_TEMPLATE = """\
请根据以下结构化风险简报数据，生成一份中文管理层摘要。

## 异常概览
- 异常数量：{anomaly_count}，其中 high={high}、medium={medium}、low={low}
- 观测窗口：基线 {baseline_window}，近期 {recent_window}
- 核心指标：{target_metric_name}（{target_metric}）相对基线变化 {target_change}

## Top 归因驱动因素
{drivers_text}

## 策略 Lab 信号
- 优先情景：{priority_scenarios}
- 最高 ROI 情景：{top_strategy}（估算 delta {estimated_delta}，ROI 倍数 {roi_ratio}）
- 正 ROI 情景数：{positive_roi_count}

## ML Baseline 信号
- 推荐建模目标：{recommended_target}
- 最优模型：{best_model}，AUC={auc}，KS={ks}，Top Decile Capture={top_decile_capture}
- 样本量：{row_count}，正样本率：{positive_rate}
- 重要说明：这是 demo 级别 baseline，AUC 0.57 反映合成数据校准局限，不代表生产建模能力

请按以下结构生成摘要：
1. 总体结论与核心指标变化（1段）
2. 主要归因信号与需要重点核查的维度（1段）
3. 策略 Lab 方向与 ROI 估算的使用边界（1段）
4. ML 信号在 demo 语境下的含义与局限（1段）
5. 下一步人工确认事项与 demo 边界声明（1段）
"""


def narrate_briefing(
    briefing: dict[str, Any],
    *,
    api_key: str | None = None,
    base_url: str = _DEFAULT_BASE_URL,
    model: str = _DEFAULT_MODEL,
) -> str:
    """Call DeepSeek API and return a Chinese management narrative string.

    Raises ValueError if no API key is available.
    Caller is responsible for catching exceptions and falling back.
    """
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError(
            "DEEPSEEK_API_KEY not found in environment. "
            "Run: export DEEPSEEK_API_KEY=<your-key>"
        )

    from openai import OpenAI  # noqa: PLC0415

    client = OpenAI(api_key=key, base_url=base_url)

    happened = briefing.get("what_happened", {})
    why = briefing.get("why", {})
    strategy = briefing.get("strategy_lab", {})
    ml = briefing.get("ml_baseline", {})
    top = strategy.get("top_strategy") or {}
    severity = happened.get("severity_counts") or {}

    drivers_lines = "\n".join(
        "- {name}={val}：contribution={contribution}，建议动作={action}".format(
            name=d.get("dimension_name", "-"),
            val=d.get("dimension_value", "-"),
            contribution=_fmt_pct(d.get("contribution_score")),
            action=d.get("recommended_action") or "-",
        )
        for d in (why.get("top_drivers") or [])[:5]
    )

    prompt = _USER_PROMPT_TEMPLATE.format(
        anomaly_count=happened.get("anomaly_count", 0),
        high=severity.get("high", 0),
        medium=severity.get("medium", 0),
        low=severity.get("low", 0),
        baseline_window=happened.get("baseline_window", "-"),
        recent_window=happened.get("recent_window", "-"),
        target_metric_name=happened.get("target_metric_name", "-"),
        target_metric=happened.get("target_metric", "-"),
        target_change=_fmt_pct(happened.get("target_relative_change")),
        drivers_text=drivers_lines or "（无驱动因素数据）",
        priority_scenarios=", ".join(
            str(s) for s in (strategy.get("priority_scenarios") or [])
        ) or "none",
        top_strategy=top.get("scenario_id", "none"),
        estimated_delta=_fmt_pct(top.get("estimated_delta")),
        roi_ratio=_fmt_num(top.get("roi_ratio")),
        positive_roi_count=strategy.get("positive_roi_count", 0),
        recommended_target=ml.get("recommended_target", "-"),
        best_model=ml.get("best_model", "-"),
        auc=_fmt_num(ml.get("auc")),
        ks=_fmt_num(ml.get("ks")),
        top_decile_capture=_fmt_pct(ml.get("top_decile_capture_rate")),
        row_count=ml.get("row_count", 0),
        positive_rate=_fmt_pct(ml.get("positive_rate")),
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1200,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def _fmt_pct(v: Any) -> str:
    if not isinstance(v, (int, float)):
        return "-"
    prefix = "+" if v > 0 else ""
    return f"{prefix}{v * 100:.2f}%"


def _fmt_num(v: Any) -> str:
    if not isinstance(v, (int, float)):
        return "-"
    return f"{v:.2f}"
