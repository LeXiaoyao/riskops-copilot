"""Collection process metric calculators."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from riskops.metrics.calculators.base import DATA_ROOT, as_date, empty_daily, read_table, safe_rate


def _process(root: Path = DATA_ROOT) -> pd.DataFrame:
    process = read_table(root, "dws", "dws_collection_process_wide_di").copy()
    process["stat_date"] = as_date(process["stat_date"])
    return process


def _actions(root: Path = DATA_ROOT) -> pd.DataFrame:
    action = read_table(root, "dwd", "dwd_collection_action_detail_di").copy()
    action["stat_date"] = as_date(action["action_date"])
    action["action_time"] = pd.to_datetime(action["action_time"])
    return action


def _valid_calls(root: Path = DATA_ROOT) -> pd.DataFrame:
    action = _actions(root)
    calls = read_table(root, "ods", "ods_call_record").copy()
    if calls.empty:
        return action.iloc[0:0].assign(duration_seconds=pd.Series(dtype=float), valid_contact_flag=pd.Series(dtype=bool))
    calls = calls[["action_id", "duration_seconds"]]
    joined = action.merge(calls, on="action_id", how="left")
    joined["duration_seconds"] = pd.to_numeric(joined["duration_seconds"], errors="coerce").fillna(0)
    joined["valid_contact_flag"] = joined["connected_flag"].astype(bool) & (joined["duration_seconds"] >= 60)
    return joined


def call_coverage_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    process = _process(root)
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    called = process.groupby("stat_date", as_index=False).agg(called_case_count=("case_id", "nunique"))
    assigned = case_status.groupby("stat_date", as_index=False).agg(assigned_case_count=("case_id", "nunique"))
    daily = assigned.merge(called, on="stat_date", how="left").fillna({"called_case_count": 0})
    daily["call_coverage_rate"] = safe_rate(daily["called_case_count"], daily["assigned_case_count"]).to_numpy()
    return daily[["stat_date", "call_coverage_rate"]]


def valid_coverage_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    valid = _valid_calls(root)
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    valid_cases = valid[valid["valid_contact_flag"]].groupby("stat_date", as_index=False).agg(valid_contact_case_count=("case_id", "nunique"))
    assigned = case_status.groupby("stat_date", as_index=False).agg(assigned_case_count=("case_id", "nunique"))
    daily = assigned.merge(valid_cases, on="stat_date", how="left").fillna({"valid_contact_case_count": 0})
    daily["valid_coverage_rate"] = safe_rate(daily["valid_contact_case_count"], daily["assigned_case_count"]).to_numpy()
    return daily[["stat_date", "valid_coverage_rate"]]


def connect_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    process = _process(root)
    daily = process.groupby("stat_date", as_index=False).agg(connected_count=("connected_count", "sum"), action_count=("action_count", "sum"))
    daily["connect_rate"] = safe_rate(daily["connected_count"], daily["action_count"]).to_numpy()
    return daily[["stat_date", "connect_rate"]]


def valid_contact_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    valid = _valid_calls(root)
    daily = valid.groupby("stat_date", as_index=False).agg(
        valid_contact_count=("valid_contact_flag", "sum"),
        connect_count=("connected_flag", "sum"),
    )
    daily["valid_contact_rate"] = safe_rate(daily["valid_contact_count"], daily["connect_count"]).to_numpy()
    return daily[["stat_date", "valid_contact_rate"]]


def first_contact_hours(root: Path = DATA_ROOT) -> pd.DataFrame:
    action = _actions(root)
    case = read_table(root, "dim", "dim_case")[["case_id", "case_create_time"]].copy()
    case["case_create_time"] = pd.to_datetime(case["case_create_time"])
    first = action.groupby(["stat_date", "case_id"], as_index=False)["action_time"].min()
    joined = first.merge(case, on="case_id", how="left")
    joined["hours"] = (joined["action_time"] - joined["case_create_time"]).dt.total_seconds() / 3600
    daily = joined.groupby("stat_date", as_index=False)["hours"].mean().rename(columns={"hours": "first_contact_hours"})
    daily["first_contact_hours"] = daily["first_contact_hours"].clip(lower=0).round(4)
    return daily[["stat_date", "first_contact_hours"]]


def ptp_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    valid = _valid_calls(root)
    daily = valid.groupby("stat_date", as_index=False).agg(ptp_count=("ptp_flag", "sum"), valid_contact_count=("valid_contact_flag", "sum"))
    daily["ptp_rate"] = safe_rate(daily["ptp_count"], daily["valid_contact_count"]).to_numpy()
    return daily[["stat_date", "ptp_rate"]]


def ptp_keep_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    process = _process(root)
    daily = process.groupby("stat_date", as_index=False).agg(
        kept_ptp_count=("ptp_fulfilled_count", "sum"),
        matured_ptp_count=("ptp_count", "sum"),
    )
    daily["ptp_keep_rate"] = safe_rate(daily["kept_ptp_count"], daily["matured_ptp_count"]).to_numpy()
    return daily[["stat_date", "ptp_keep_rate"]]


def avg_call_duration_per_call(root: Path = DATA_ROOT) -> pd.DataFrame:
    valid = _valid_calls(root)
    call_rows = valid[valid["duration_seconds"] > 0]
    if call_rows.empty:
        return empty_daily("avg_call_duration_per_call")
    daily = call_rows.groupby("stat_date", as_index=False).agg(
        duration_sum=("duration_seconds", "sum"),
        call_count=("action_id", "count"),
    )
    daily["avg_call_duration_per_call"] = np.where(daily["call_count"] > 0, daily["duration_sum"] / daily["call_count"], 0).round(4)
    return daily[["stat_date", "avg_call_duration_per_call"]]


def avg_call_duration_per_collector(root: Path = DATA_ROOT) -> pd.DataFrame:
    valid = _valid_calls(root)
    call_rows = valid[valid["duration_seconds"] > 0]
    if call_rows.empty:
        return empty_daily("avg_call_duration_per_collector")
    daily = call_rows.groupby("stat_date", as_index=False).agg(
        duration_sum=("duration_seconds", "sum"),
        active_collector_count=("collector_id", "nunique"),
    )
    daily["avg_call_duration_per_collector"] = np.where(
        daily["active_collector_count"] > 0,
        daily["duration_sum"] / daily["active_collector_count"],
        0,
    ).round(4)
    return daily[["stat_date", "avg_call_duration_per_collector"]]


def collector_productivity(root: Path = DATA_ROOT) -> pd.DataFrame:
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    daily = case_status.groupby("stat_date", as_index=False).agg(
        repay_amount=("repaid_amount", "sum"),
        active_collector_count=("collector_id", "nunique"),
    )
    daily["collector_productivity"] = np.where(daily["active_collector_count"] > 0, daily["repay_amount"] / daily["active_collector_count"], 0).round(4)
    return daily[["stat_date", "collector_productivity"]]


COLLECTION_METRICS = {
    "call_coverage_rate": call_coverage_rate,
    "valid_coverage_rate": valid_coverage_rate,
    "connect_rate": connect_rate,
    "valid_contact_rate": valid_contact_rate,
    "first_contact_hours": first_contact_hours,
    "ptp_rate": ptp_rate,
    "ptp_keep_rate": ptp_keep_rate,
    "avg_call_duration_per_call": avg_call_duration_per_call,
    "avg_call_duration_per_collector": avg_call_duration_per_collector,
    "collector_productivity": collector_productivity,
}
