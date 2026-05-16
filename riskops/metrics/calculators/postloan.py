"""Post-loan result metric calculators."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from riskops.metrics.calculators.base import DATA_ROOT, as_date, empty_daily, read_table, safe_rate


def _due(root: Path = DATA_ROOT) -> pd.DataFrame:
    due = read_table(root, "dwd", "dwd_due_plan_detail_di").copy()
    due["stat_date"] = as_date(due["stat_date"])
    return due


def _repay(root: Path = DATA_ROOT) -> pd.DataFrame:
    repay = read_table(root, "dwd", "dwd_repayment_detail_di").copy()
    repay["repay_time"] = pd.to_datetime(repay["repay_time"])
    return repay


def _window_recovery(days: int, metric_code: str, root: Path = DATA_ROOT) -> pd.DataFrame:
    due = _due(root)
    repay = _repay(root)
    if due.empty:
        return empty_daily(metric_code)
    due["due_date_ts"] = pd.to_datetime(due["due_date"])
    joined = due[["stat_date", "plan_id", "due_date_ts", "outstanding_amount"]].merge(
        repay[["plan_id", "repay_time", "repay_amount"]], on="plan_id", how="left"
    )
    in_window = joined["repay_time"].notna() & (joined["repay_time"] <= joined["due_date_ts"] + pd.Timedelta(days=days))
    joined["window_repay"] = joined["repay_amount"].where(in_window, 0.0)
    daily = joined.groupby("stat_date", as_index=False).agg(
        numerator=("window_repay", "sum"),
        denominator=("outstanding_amount", "sum"),
    )
    daily[metric_code] = safe_rate(daily["numerator"], daily["denominator"]).to_numpy()
    return daily[["stat_date", metric_code]]


def due_account_count(root: Path = DATA_ROOT) -> pd.DataFrame:
    due = _due(root)
    return due.groupby("stat_date", as_index=False)["customer_id"].nunique().rename(columns={"customer_id": "due_account_count"})


def due_loan_count(root: Path = DATA_ROOT) -> pd.DataFrame:
    due = _due(root)
    return due.groupby("stat_date", as_index=False)["loan_id"].nunique().rename(columns={"loan_id": "due_loan_count"})


def due_total_amount(root: Path = DATA_ROOT) -> pd.DataFrame:
    due = _due(root)
    return due.groupby("stat_date", as_index=False)["due_amount"].sum().rename(columns={"due_amount": "due_total_amount"})


def collection_entry_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    due_accounts = due_account_count(root)
    case = read_table(root, "dim", "dim_case").copy()
    case["stat_date"] = as_date(case["case_create_time"])
    entry = case.groupby("stat_date", as_index=False)["customer_id"].nunique().rename(columns={"customer_id": "entry_accounts"})
    daily = due_accounts.merge(entry, on="stat_date", how="left").fillna({"entry_accounts": 0})
    daily["collection_entry_rate"] = safe_rate(daily["entry_accounts"], daily["due_account_count"]).to_numpy()
    return daily[["stat_date", "collection_entry_rate"]]


def recovery_rate_d7(root: Path = DATA_ROOT) -> pd.DataFrame:
    return _window_recovery(7, "recovery_rate_d7", root)


def recovery_rate_d15(root: Path = DATA_ROOT) -> pd.DataFrame:
    return _window_recovery(15, "recovery_rate_d15", root)


def recovery_rate_d30(root: Path = DATA_ROOT) -> pd.DataFrame:
    return _window_recovery(30, "recovery_rate_d30", root)


def m1_recovery_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    loan = read_table(root, "dws", "dws_loan_status_snapshot_di").copy()
    loan["stat_date"] = as_date(loan["stat_date"])
    m1 = loan[loan["dpd_bucket"].eq("M1")]
    if m1.empty:
        return empty_daily("m1_recovery_rate")
    daily = m1.groupby("stat_date", as_index=False).agg(
        numerator=("repaid_amount_d7", "sum"),
        denominator=("due_amount", "sum"),
    )
    daily["m1_recovery_rate"] = safe_rate(daily["numerator"], daily["denominator"]).to_numpy()
    return daily[["stat_date", "m1_recovery_rate"]]


POSTLOAN_METRICS = {
    "due_account_count": due_account_count,
    "due_loan_count": due_loan_count,
    "due_total_amount": due_total_amount,
    "collection_entry_rate": collection_entry_rate,
    "recovery_rate_d7": recovery_rate_d7,
    "recovery_rate_d15": recovery_rate_d15,
    "recovery_rate_d30": recovery_rate_d30,
    "m1_recovery_rate": m1_recovery_rate,
}
