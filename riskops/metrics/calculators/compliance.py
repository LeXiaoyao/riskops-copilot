"""Compliance and complaint metric calculators."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from riskops.metrics.calculators.base import DATA_ROOT, as_date, read_table, safe_rate


def _complaint(root: Path = DATA_ROOT) -> pd.DataFrame:
    complaint = read_table(root, "dwd", "dwd_complaint_detail_di").copy()
    complaint["stat_date"] = as_date(complaint["complaint_date"])
    return complaint


def complaint_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    complaint = _complaint(root)
    active = case_status.groupby("stat_date", as_index=False).agg(active_case_count=("case_id", "nunique"))
    comp = complaint.groupby("stat_date", as_index=False).agg(complaint_case_count=("case_id", "nunique"))
    daily = active.merge(comp, on="stat_date", how="left").fillna({"complaint_case_count": 0})
    daily["complaint_rate"] = safe_rate(daily["complaint_case_count"], daily["active_case_count"]).to_numpy()
    return daily[["stat_date", "complaint_rate"]]


def complaint_per_10k_cases(root: Path = DATA_ROOT) -> pd.DataFrame:
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    complaint = _complaint(root)
    active = case_status.groupby("stat_date", as_index=False).agg(active_case_count=("case_id", "nunique"))
    comp = complaint.groupby("stat_date", as_index=False).agg(complaint_count=("complaint_id", "count"))
    daily = active.merge(comp, on="stat_date", how="left").fillna({"complaint_count": 0})
    daily["complaint_per_10k_cases"] = (daily["complaint_count"] / daily["active_case_count"].where(daily["active_case_count"] > 0, pd.NA) * 10000).fillna(0).round(4)
    return daily[["stat_date", "complaint_per_10k_cases"]]


def risk_phrase_hit_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    action = read_table(root, "dwd", "dwd_collection_action_detail_di").copy()
    action["stat_date"] = as_date(action["action_date"])
    checked = action[action["action_type"].isin(["SMS", "CALL", "AI_OUTBOUND"])].copy()
    checked["risk_hit"] = checked["template_id"].fillna("").eq("TPL_RISK_NOTICE")
    daily = checked.groupby("stat_date", as_index=False).agg(
        risk_phrase_hit_count=("risk_hit", "sum"),
        qa_checked_count=("action_id", "count"),
    )
    daily["risk_phrase_hit_rate"] = safe_rate(daily["risk_phrase_hit_count"], daily["qa_checked_count"]).to_numpy()
    return daily[["stat_date", "risk_phrase_hit_rate"]]


def qa_fail_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    action = read_table(root, "dwd", "dwd_collection_action_detail_di").copy()
    action["stat_date"] = as_date(action["action_date"])
    complaint = _complaint(root)
    checked = action[action["action_type"].isin(["CALL", "AI_OUTBOUND"])].groupby("stat_date", as_index=False).agg(
        qa_checked_call_count=("action_id", "count")
    )
    fail = complaint[complaint["complaint_level"].isin(["MEDIUM", "HIGH"])].groupby("stat_date", as_index=False).agg(
        qa_fail_call_count=("complaint_id", "count")
    )
    daily = checked.merge(fail, on="stat_date", how="left").fillna({"qa_fail_call_count": 0})
    daily["qa_fail_rate"] = safe_rate(daily["qa_fail_call_count"], daily["qa_checked_call_count"]).to_numpy()
    return daily[["stat_date", "qa_fail_rate"]]


def over_frequency_contact_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    action = read_table(root, "dwd", "dwd_collection_action_detail_di").copy()
    action["stat_date"] = as_date(action["action_date"])
    by_case = action.groupby(["stat_date", "case_id"], as_index=False).agg(action_count=("action_id", "count"))
    daily = by_case.groupby("stat_date", as_index=False).agg(
        over_frequency_case_count=("action_count", lambda x: (x > 3).sum()),
        contacted_case_count=("case_id", "count"),
    )
    daily["over_frequency_contact_rate"] = safe_rate(daily["over_frequency_case_count"], daily["contacted_case_count"]).to_numpy()
    return daily[["stat_date", "over_frequency_contact_rate"]]


COMPLIANCE_METRICS = {
    "complaint_rate": complaint_rate,
    "complaint_per_10k_cases": complaint_per_10k_cases,
    "risk_phrase_hit_rate": risk_phrase_hit_rate,
    "qa_fail_rate": qa_fail_rate,
    "over_frequency_contact_rate": over_frequency_contact_rate,
}
