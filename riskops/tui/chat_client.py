"""DeepSeek streaming chat client for the RiskOps TUI."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

from riskops.tui.context_loader import load_context

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
                token = _extract_delta(data)
                if token:
                    yield token
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API 请求失败：HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"DeepSeek API 连接失败：{exc.reason}") from exc


def _extract_delta(data: str) -> str:
    payload: Any = json.loads(data)
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not choices:
        return ""
    delta = choices[0].get("delta") if isinstance(choices[0], dict) else None
    if not isinstance(delta, dict):
        return ""
    content = delta.get("content")
    return content if isinstance(content, str) else ""
