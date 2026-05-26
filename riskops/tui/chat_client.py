"""DeepSeek streaming chat client for the RiskOps TUI."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

from riskops.tui.context_loader import load_context
from riskops.tui.tool_schemas import TOOL_SCHEMAS
from riskops.tui.tools import call_tool

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
SYSTEM_PROMPT_TEMPLATE = """你是 RiskOps Copilot，一个贷后风险运营 AI 助手。
以下是当前项目的数据摘要，请基于此回答用户问题。
如数据不足以回答，请明确说明。
所有建议仅供参考，不构成自动决策。

{context}"""


def stream_chat(messages: list[dict], model: str, api_key: str) -> Iterator[str]:
    context = load_context()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(context=context)},
            *messages,
        ],
        "stream": True,
    }
    for chunk in _post_stream(payload, api_key):
        token = _extract_delta(chunk)
        if token:
            yield token


def stream_chat_with_tools(
    messages: list[dict],
    model: str,
    api_key: str,
) -> Iterator[str | dict[str, Any]]:
    context = load_context()
    working_messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(context=context)},
        *messages,
    ]
    first_payload = {
        "model": model,
        "messages": working_messages,
        "tools": TOOL_SCHEMAS,
        "tool_choice": "auto",
        "stream": True,
    }

    answer_parts: list[str] = []
    tool_calls: dict[int, dict[str, Any]] = {}
    finish_reason = None
    for chunk in _post_stream(first_payload, api_key):
        choice = _first_choice(chunk)
        if not choice:
            continue
        finish_reason = choice.get("finish_reason") or finish_reason
        delta = choice.get("delta") if isinstance(choice.get("delta"), dict) else {}
        content = delta.get("content")
        if isinstance(content, str) and content:
            answer_parts.append(content)
            yield content
        _merge_tool_calls(tool_calls, delta.get("tool_calls"))

    if finish_reason != "tool_calls" and not tool_calls:
        return

    assistant_tool_calls = _finalize_tool_calls(tool_calls)
    working_messages.append(
        {
            "role": "assistant",
            "content": "".join(answer_parts) or None,
            "tool_calls": assistant_tool_calls,
        }
    )

    for tool_call in assistant_tool_calls:
        function = tool_call.get("function", {})
        tool_name = function.get("name")
        params = _parse_tool_arguments(function.get("arguments"))
        if not isinstance(tool_name, str):
            continue
        result = call_tool(tool_name, params)
        yield {
            "type": "tool_call",
            "tool": tool_name,
            "params": params,
            "row_count": result["row_count"],
        }
        working_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    second_payload = {
        "model": model,
        "messages": working_messages,
        "stream": True,
    }
    for chunk in _post_stream(second_payload, api_key):
        token = _extract_delta(chunk)
        if token:
            yield token


def _post_stream(payload: dict[str, Any], api_key: str) -> Iterator[dict[str, Any]]:
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
        with urllib.request.urlopen(request, timeout=90) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    break
                yield json.loads(data)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API 请求失败：HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"DeepSeek API 连接失败：{exc.reason}") from exc


def _extract_delta(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not choices:
        return ""
    delta = choices[0].get("delta") if isinstance(choices[0], dict) else None
    if not isinstance(delta, dict):
        return ""
    content = delta.get("content")
    return content if isinstance(content, str) else ""


def _first_choice(payload: dict[str, Any]) -> dict[str, Any] | None:
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not choices or not isinstance(choices[0], dict):
        return None
    return choices[0]


def _merge_tool_calls(
    tool_calls: dict[int, dict[str, Any]],
    delta_tool_calls: Any,
) -> None:
    if not isinstance(delta_tool_calls, list):
        return
    for item in delta_tool_calls:
        if not isinstance(item, dict):
            continue
        index = int(item.get("index", len(tool_calls)))
        current = tool_calls.setdefault(
            index,
            {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
        )
        if item.get("id"):
            current["id"] = item["id"]
        if item.get("type"):
            current["type"] = item["type"]
        function_delta = item.get("function")
        if isinstance(function_delta, dict):
            function = current["function"]
            if function_delta.get("name"):
                function["name"] += function_delta["name"]
            if function_delta.get("arguments"):
                function["arguments"] += function_delta["arguments"]


def _finalize_tool_calls(tool_calls: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    finalized = []
    for index, item in sorted(tool_calls.items()):
        tool_call = {
            "id": item.get("id") or f"tool_call_{index}",
            "type": item.get("type") or "function",
            "function": {
                "name": item.get("function", {}).get("name", ""),
                "arguments": item.get("function", {}).get("arguments", "{}"),
            },
        }
        finalized.append(tool_call)
    return finalized


def _parse_tool_arguments(arguments: Any) -> dict[str, Any]:
    if not isinstance(arguments, str) or not arguments.strip():
        return {}
    try:
        parsed = json.loads(arguments)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
