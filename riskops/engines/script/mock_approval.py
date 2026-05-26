"""Mock approval and audit log for script drafts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
APPROVAL_LOG_PATH = ROOT / "outputs" / "script" / "approval_log.jsonl"


def approve_and_log(draft: dict[str, Any], approved_by: str = "demo_user") -> dict[str, str]:
    """Append an approved draft record to the mock audit log."""

    _write_log(draft, actor=approved_by, status="approved")
    return {"status": "approved", "log_path": "outputs/script/approval_log.jsonl"}


def reject_draft(draft: dict[str, Any], reason: str, rejected_by: str = "demo_user") -> dict[str, str]:
    """Append a rejected draft record to the mock audit log."""

    _write_log(draft, actor=rejected_by, status="rejected", reason=reason)
    return {"status": "rejected", "log_path": "outputs/script/approval_log.jsonl"}


def _write_log(draft: dict[str, Any], *, actor: str, status: str, reason: str | None = None) -> None:
    APPROVAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "draft_id": draft.get("draft_id"),
        "case_id": draft.get("case_id"),
        "channel": draft.get("channel"),
        "draft_content": draft.get("draft_content"),
        "risk_level": draft.get("risk_level"),
        "approved_by": actor if status == "approved" else None,
        "rejected_by": actor if status == "rejected" else None,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approval_status": status,
        "mock_send_status": "mock_sent" if status == "approved" else "not_sent",
    }
    if reason:
        record["reason"] = reason
    with APPROVAL_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
