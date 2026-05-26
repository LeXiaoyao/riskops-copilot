"""Risk analyst agent backed by DeepSeek function calling."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from riskops.tui.chat_client import stream_chat_with_tools
from riskops.tui.tool_schemas import TOOL_SCHEMAS
from riskops.tui.tools import (
    get_data_overview,
    query_anomalies,
    query_case_detail,
    query_collection_process,
    query_collector_performance,
    query_recovery_rate,
    query_roi_scenarios,
    query_segment_breakdown,
    query_top_drivers,
    query_vendor_performance,
)

_QUERY_FUNCTIONS = (
    query_recovery_rate,
    query_anomalies,
    query_top_drivers,
    query_roi_scenarios,
    query_vendor_performance,
    query_collector_performance,
    query_segment_breakdown,
    query_case_detail,
    query_collection_process,
    get_data_overview,
)

FALLBACK_SYSTEM = """你是 RiskOps 贷后风险分析专家。
你可以调用数据查询工具获取真实合成数据进行分析。
分析原则：
1. 先调工具取数，再基于数据给结论，不臆造
2. 先结论后证据，简洁中文，像策略分析师
3. 从四个角度分析：资产结构/过程执行/资源配置/策略效果
4. 数据不足时明确说明，不补充假设
5. 所有数据基于合成数据，不代表真实业务决策
输出格式：Markdown，适合终端显示"""


class RiskAnalystAgent:
    display_name = "风险分析专家"
    TOOLS = TOOL_SCHEMAS

    def __init__(self, api_key: str | None, model: str = "deepseek-chat") -> None:
        self.api_key = api_key
        self.model = model
        self.system_prompt = _read_prompt("risk_analyst.txt", FALLBACK_SYSTEM)

    def run(self, message: str) -> Iterator[str]:
        if not self.api_key:
            yield "请先设置 DEEPSEEK_API_KEY 后再进行风险分析。\n"
            return

        events = stream_chat_with_tools(
            [{"role": "user", "content": message}],
            self.model,
            self.api_key,
            system_prompt=self.system_prompt,
            tools=self.TOOLS,
        )
        for event in events:
            if isinstance(event, dict) and event.get("type") == "tool_call":
                yield _format_tool_event(event)
            elif isinstance(event, str):
                yield event


def _read_prompt(filename: str, fallback: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / filename
    if not path.exists():
        return fallback
    content = path.read_text(encoding="utf-8").strip()
    return content or fallback


def _format_tool_event(event: dict[str, Any]) -> str:
    tool = event.get("tool", "unknown")
    params = event.get("params", {})
    row_count = event.get("row_count", 0)
    param_text = ", ".join(f"{key}={value}" for key, value in params.items())
    return f"\n[工具调用] {tool}({param_text}) → 返回 {row_count} 行\n\n"
