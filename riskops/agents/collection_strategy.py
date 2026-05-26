"""Collection strategy agent for safe script drafts and process analysis."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from riskops.engines.script.case_context import load_case_context
from riskops.engines.script.frequency_checker import check_frequency
from riskops.engines.script.mock_approval import approve_and_log
from riskops.engines.script.script_engine import generate_script_draft
from riskops.tui.chat_client import stream_chat_with_tools
from riskops.tui.tool_schemas import TOOL_SCHEMAS

FALLBACK_SYSTEM = """你是 RiskOps 催收策略专家，专注于分案策略、触达策略、减免策略和话术草稿。
可以根据案件上下文生成合规话术草稿，所有草稿必须经过人工审批才能发送。
严禁威胁/辱骂/骚扰/冒充司法/骚扰第三方等违规行为。"""

TOOL_NAMES = {
    "query_case_detail",
    "query_vendor_performance",
    "query_roi_scenarios",
    "query_collection_process",
}


class CollectionStrategyAgent:
    display_name = "催收策略专家"
    TOOLS = [schema for schema in TOOL_SCHEMAS if schema["function"]["name"] in TOOL_NAMES]

    def __init__(self, api_key: str | None, model: str = "deepseek-chat") -> None:
        self.api_key = api_key
        self.model = model
        self.system_prompt = _read_prompt("collection_strategy.txt", FALLBACK_SYSTEM)

    def run(self, message: str) -> Iterator[str]:
        case_id = _extract_case_id(message)
        if case_id:
            if not self.api_key:
                yield "未设置 DEEPSEEK_API_KEY，将使用本地规则生成未润色话术草稿。\n\n"
            yield from self._run_case_script(case_id)
            return

        if not self.api_key:
            yield "请先设置 DEEPSEEK_API_KEY，或在问题中提供 CASE 编号生成本地话术草稿。\n"
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

    def _run_case_script(self, case_id: str) -> Iterator[str]:
        try:
            context = load_case_context(case_id)
            frequency = check_frequency(case_id, "sms", context)
            try:
                draft = generate_script_draft(case_id, "sms", context, api_key=self.api_key)
            except Exception:
                draft = generate_script_draft(case_id, "sms", context, api_key=None)
        except (FileNotFoundError, ValueError) as exc:
            yield f"无法生成话术草稿：{exc}\n"
            return

        compliance = draft.get("compliance_scan", {})
        yield "### 话术草稿\n"
        yield f"{draft.get('draft_content', '')}\n\n"
        yield "### 合规与频次\n"
        yield f"- 合规风险：{compliance.get('risk_level', 'unknown')}\n"
        yield f"- 违规命中数：{compliance.get('violation_count', 0)}\n"
        yield f"- 频次允许：{'是' if frequency.get('allowed') else '否'}\n"
        yield f"- 今日短信触达：{frequency.get('today_count')}/{frequency.get('daily_limit')}\n"
        yield f"- 近7日短信触达：{frequency.get('week_count')}/{frequency.get('weekly_limit')}\n"
        if frequency.get("block_reason"):
            yield f"- 阻断原因：{frequency['block_reason']}\n"
        yield f"- 综合风险等级：{draft.get('risk_level', 'unknown')}\n"
        yield f"- 审批状态：{draft.get('approval_status', 'pending')}，未真实外发\n"


def _extract_case_id(message: str) -> str | None:
    match = re.search(r"\bCASE-?\d+\b", message, flags=re.IGNORECASE)
    return match.group(0).upper() if match else None


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


__all__ = ["CollectionStrategyAgent", "approve_and_log"]
