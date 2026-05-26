"""Deterministic script recommendation engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from riskops.engines.qc.compliance_scanner import scan_text
from riskops.engines.script.frequency_checker import check_frequency

SCRIPT_TEMPLATES = {
    "first_overdue": "【{company}】尊敬的客户，您有一笔借款已进入逾期，应还金额 ¥{amount}。请尽快联系我们安排还款，避免影响信用记录。如已还款请忽略。",
    "d1_gentle": "【{company}】您好，您的借款 ¥{amount} 已逾期1天。如有困难可联系我们申请方案。",
    "d7_solution": "【{company}】您的借款 ¥{amount} 已逾期7天。现可申请分期减免（最高20%），请于今日18:00前联系 4001234567 或回复1协商。",
    "d15_reduction": "【{company}】您的借款 ¥{amount} 已逾期较长时间。当前可提交减免或分期申请，请在工作时间联系 4001234567 协商还款安排。",
    "ptp_reminder": "【{company}】温馨提醒，您此前约定的还款安排即将到期，应还金额 ¥{amount}。如需调整方案，请及时联系 4001234567。",
    "ptp_followup": "【{company}】您此前约定的还款安排尚未完成，应还金额 ¥{amount}。如遇困难，请联系 4001234567 重新确认可行方案。",
    "lost_contact": "【{company}】您好，关于您名下借款 ¥{amount} 的还款安排，我们需要与您确认。请在方便时联系 4001234567。",
    "complaint_sensitive": "【{company}】您好，关于您名下借款 ¥{amount}，如需还款协商或服务支持，请通过官方渠道 4001234567 联系我们。",
    "high_risk_manual": "【{company}】您好，您的借款 ¥{amount} 需进一步人工核实还款安排。请联系 4001234567，我们将由专员协助处理。",
    "post_payment": "【{company}】您好，系统已关注到您的还款处理状态。如已完成还款请忽略；如需凭证确认，请联系 4001234567。",
}

SYSTEM_PROMPT = (
    "你是合规催收话术优化助手。在不违反合规红线的前提下，"
    "根据案件背景对草稿做简短润色，保持简洁专业。不得添加威胁/施压内容。"
)


def generate_script_draft(
    case_id: str,
    channel: str,
    context: dict[str, Any],
    api_key: str | None = None,
) -> dict[str, Any]:
    """Generate a deterministic script draft and attach risk checks."""

    script_type = choose_script_type(context)
    template_draft = SCRIPT_TEMPLATES[script_type].format(
        company="XX金融",
        amount=_format_amount(context.get("outstanding_amount", 0.0)),
    )
    draft_content = template_draft
    llm_polished = False

    if api_key:
        polished = _polish_with_deepseek(template_draft, context, api_key)
        if polished:
            draft_content = polished
            llm_polished = True

    compliance_scan = scan_text(draft_content)
    frequency_check = check_frequency(case_id, channel, context)
    risk_level = _combined_risk_level(compliance_scan, frequency_check)

    return {
        "draft_id": f"DRAFT-{context.get('case_id', case_id)}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "case_id": context.get("case_id", case_id),
        "channel": frequency_check["channel"],
        "script_type": script_type,
        "draft_content": draft_content,
        "llm_polished": llm_polished,
        "compliance_scan": compliance_scan,
        "frequency_check": frequency_check,
        "risk_level": risk_level,
        "supervisor_review_required": bool(context.get("protect_flag")) or compliance_scan.get("risk_level") == "high",
        "approval_status": "pending",
        "note": "Mock draft — 不做真实外发，需人工确认",
    }


def choose_script_type(context: dict[str, Any]) -> str:
    if context.get("protect_flag") or context.get("complaint_flag") or context.get("sensitive_flag"):
        return "complaint_sensitive"
    if _as_float(context.get("outstanding_amount")) <= 0:
        return "post_payment"
    if context.get("ptp_fulfilled") is False:
        return "ptp_followup"
    if context.get("last_ptp_date"):
        return "ptp_reminder"
    if _as_float(context.get("recent_connect_rate")) <= 0 and int(context.get("recent_action_count_7d", 0) or 0) >= 3:
        return "lost_contact"
    if str(context.get("risk_level", "")).upper() in {"D", "HIGH"} or str(context.get("initial_dpd_bucket", "")).upper() == "M3+":
        return "high_risk_manual"
    bucket = str(context.get("initial_dpd_bucket", "")).upper()
    if bucket == "M2":
        return "d15_reduction"
    if bucket == "M1":
        return "d7_solution"
    if bucket == "CURRENT":
        return "post_payment"
    return "first_overdue"


def _polish_with_deepseek(template_draft: str, context: dict[str, Any], api_key: str) -> str | None:
    from openai import OpenAI  # noqa: PLC0415

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"案件背景：{_context_summary(context)}\n草稿：{template_draft}\n请优化："},
        ],
        max_tokens=400,
        temperature=0.2,
    )
    content = response.choices[0].message.content or ""
    return content.strip() or None


def _context_summary(context: dict[str, Any]) -> str:
    safe_keys = [
        "case_id",
        "customer_id_hash",
        "initial_dpd_bucket",
        "outstanding_amount",
        "risk_level",
        "protect_flag",
        "complaint_flag",
        "sensitive_flag",
        "recent_action_count_7d",
        "recent_sms_count_7d",
        "recent_connect_rate",
        "current_vendor_id",
        "current_line_id",
    ]
    return "；".join(f"{key}={context.get(key)}" for key in safe_keys)


def _combined_risk_level(compliance_scan: dict[str, Any], frequency_check: dict[str, Any]) -> str:
    compliance_level = compliance_scan.get("risk_level")
    if compliance_level == "high" or not frequency_check.get("allowed", False):
        return "high"
    if compliance_level == "medium":
        return "medium"
    return "low"


def _format_amount(value: Any) -> str:
    amount = _as_float(value)
    if amount.is_integer():
        return f"{amount:,.0f}"
    return f"{amount:,.2f}"


def _as_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0
