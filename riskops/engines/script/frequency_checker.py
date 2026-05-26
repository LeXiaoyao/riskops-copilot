"""Frequency checks for script recommendation drafts."""

from __future__ import annotations

from typing import Any

CHANNEL_LIMITS = {
    "sms": {"daily": 2, "weekly": 5},
    "ai_call": {"daily": 3, "weekly": 10},
    "manual": {"daily": 5, "weekly": 20},
}


def check_frequency(case_id: str, channel: str, context: dict[str, Any]) -> dict[str, Any]:
    """Check demo contact frequency for one case and channel."""

    normalized_channel = _normalize_channel(channel)
    if normalized_channel not in CHANNEL_LIMITS:
        raise ValueError(f"unsupported channel: {channel}")

    limits = CHANNEL_LIMITS[normalized_channel]
    counts = _counts_for_channel(normalized_channel, context)
    today_count = int(counts["today"])
    week_count = int(counts["week"])

    block_reason = None
    if today_count >= limits["daily"]:
        block_reason = f"{case_id} {normalized_channel} 今日触达 {today_count} 次，已达到上限 {limits['daily']} 次"
    elif week_count >= limits["weekly"]:
        block_reason = f"{case_id} {normalized_channel} 近7日触达 {week_count} 次，已达到上限 {limits['weekly']} 次"

    return {
        "channel": normalized_channel,
        "today_count": today_count,
        "week_count": week_count,
        "daily_limit": limits["daily"],
        "weekly_limit": limits["weekly"],
        "allowed": block_reason is None,
        "block_reason": block_reason,
    }


def _normalize_channel(channel: str) -> str:
    value = str(channel).strip().lower()
    aliases = {"sms": "sms", "ai_outbound": "ai_call", "ai_call": "ai_call", "manual": "manual", "call": "manual"}
    return aliases.get(value, value)


def _counts_for_channel(channel: str, context: dict[str, Any]) -> dict[str, int]:
    frequency_counts = context.get("_frequency_counts")
    if isinstance(frequency_counts, dict) and isinstance(frequency_counts.get(channel), dict):
        channel_counts = frequency_counts[channel]
        return {
            "today": int(channel_counts.get("today", 0) or 0),
            "week": int(channel_counts.get("week", 0) or 0),
        }
    if channel == "sms":
        return {
            "today": int(context.get("today_sms_count", 0) or 0),
            "week": int(context.get("recent_sms_count_7d", 0) or 0),
        }
    return {
        "today": int(context.get("today_action_count", 0) or 0),
        "week": int(context.get("recent_action_count_7d", 0) or 0),
    }
