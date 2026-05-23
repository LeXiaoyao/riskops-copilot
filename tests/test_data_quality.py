from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from riskops.engines.model_lab.ml_dataset import build_d7_recovery_dataset
from scripts.validate_data_quality import (
    DATA_ROOT,
    validate_case_mapping,
    validate_dates,
    validate_dim_pk,
    validate_foreign_keys,
    validate_non_negative_amounts,
    validate_privacy,
    validate_rates,
    validate_snapshots,
)


ROOT = Path(__file__).resolve().parents[1]


def data_is_available() -> bool:
    return (DATA_ROOT / "dim" / "dim_customer.parquet").exists() and (
        DATA_ROOT / "ads" / "ads_postloan_dashboard_di.parquet"
    ).exists()


@pytest.mark.skipif(not data_is_available(), reason="synthetic data has not been generated and built")
def test_m1_data_quality_checks_pass() -> None:
    validate_dim_pk(DATA_ROOT)
    validate_foreign_keys(DATA_ROOT)
    validate_non_negative_amounts(DATA_ROOT)
    validate_dates(DATA_ROOT)
    validate_privacy(DATA_ROOT)
    validate_rates(DATA_ROOT)
    validate_case_mapping(DATA_ROOT)
    validate_snapshots(DATA_ROOT)


@pytest.mark.skipif(not data_is_available(), reason="synthetic data has not been generated and built")
def test_loan_daily_snapshot_repayment_state_foundation() -> None:
    loan_snapshot = pd.read_parquet(DATA_ROOT / "ods" / "ods_loan_daily_snapshot.parquet")
    plan = pd.read_parquet(DATA_ROOT / "ods" / "ods_repayment_plan.parquet")
    repayment = pd.read_parquet(DATA_ROOT / "ods" / "ods_repayment_detail.parquet")

    assert (loan_snapshot["dpd"] >= 0).all()
    assert (loan_snapshot["outstanding_amount"] >= 0).all()
    assert loan_snapshot["loan_status"].notna().all()
    assert (loan_snapshot.loc[loan_snapshot["outstanding_amount"].le(0), "dpd"] == 0).all()

    stat_dates = pd.to_datetime(loan_snapshot["stat_date"])
    loan_state = loan_snapshot.assign(stat_date=stat_dates).merge(
        plan[["loan_id", "due_amount"]], on="loan_id", how="left", validate="many_to_one"
    )
    repayment = repayment[repayment["repay_status"].eq("SUCCESS")].copy()
    repayment["repay_date"] = pd.to_datetime(repayment["repay_time"]).dt.normalize()
    joined = loan_state.merge(
        repayment[["loan_id", "repay_date", "repay_amount"]], on="loan_id", how="left"
    )
    joined["repay_amount_until_stat_date"] = np.where(
        joined["repay_date"].notna() & (joined["repay_date"] <= joined["stat_date"]),
        joined["repay_amount"],
        0.0,
    )
    expected = (
        joined.groupby(["stat_date", "loan_id"], as_index=False)
        .agg(
            due_amount=("due_amount", "first"),
            cumulative_repaid=("repay_amount_until_stat_date", "sum"),
        )
    )
    expected["expected_outstanding_amount"] = (expected["due_amount"] - expected["cumulative_repaid"]).clip(lower=0).round(2)
    checked = loan_state.merge(expected[["stat_date", "loan_id", "expected_outstanding_amount"]], on=["stat_date", "loan_id"])
    assert np.allclose(checked["outstanding_amount"], checked["expected_outstanding_amount"], atol=0.01)

    repaid_loan_ids = set(repayment["loan_id"])
    after_repayment = loan_snapshot[loan_snapshot["loan_id"].isin(repaid_loan_ids)].sort_values(["loan_id", "stat_date"])
    outstanding_delta = after_repayment.groupby("loan_id")["outstanding_amount"].diff().fillna(0)
    increases = outstanding_delta > 0.01
    assert not increases.any()
    assert (outstanding_delta < -0.01).any()

    prior_outstanding = after_repayment.groupby("loan_id")["outstanding_amount"].shift()
    cleared_after_repayment = after_repayment["outstanding_amount"].le(0.01) & prior_outstanding.gt(0.01)
    assert cleared_after_repayment.any()


@pytest.mark.skipif(not data_is_available(), reason="synthetic data has not been generated and built")
def test_case_daily_snapshot_state_foundation() -> None:
    case_snapshot = pd.read_parquet(DATA_ROOT / "ods" / "ods_case_daily_snapshot.parquet")

    assert not case_snapshot.duplicated(["case_id", "stat_date"]).any()
    assert (case_snapshot["outstanding_amount"] >= 0).all()
    assert case_snapshot["case_status"].notna().all()
    closed = case_snapshot["case_status"].isin(["cured", "closed"])
    assert (case_snapshot.loc[closed, "outstanding_amount"] <= 0.01).all()
    assert case_snapshot["case_status"].eq("partially_paid").any()
    assert closed.any()


@pytest.mark.skipif(not data_is_available(), reason="synthetic data has not been generated and built")
def test_customer_daily_snapshot_state_foundation() -> None:
    customer_snapshot = pd.read_parquet(DATA_ROOT / "ods" / "ods_customer_daily_snapshot.parquet")
    case_snapshot = pd.read_parquet(DATA_ROOT / "ods" / "ods_case_daily_snapshot.parquet")

    assert not customer_snapshot.duplicated(["customer_id", "stat_date"]).any()
    assert (customer_snapshot["total_outstanding_amount"] >= 0).all()
    assert (customer_snapshot["max_dpd"] >= 0).all()
    assert (customer_snapshot.loc[customer_snapshot["total_outstanding_amount"].le(0), "max_dpd"] == 0).all()
    assert customer_snapshot["total_outstanding_amount"].le(0.01).any()

    case_outstanding = (
        case_snapshot.groupby(["stat_date", "customer_id"], as_index=False)["outstanding_amount"]
        .sum()
        .rename(columns={"outstanding_amount": "case_total_outstanding_amount"})
    )
    checked = customer_snapshot.merge(case_outstanding, on=["stat_date", "customer_id"], how="left")
    assert np.allclose(
        checked["total_outstanding_amount"],
        checked["case_total_outstanding_amount"].fillna(0),
        atol=0.01,
    )


@pytest.mark.skipif(not data_is_available(), reason="synthetic data has not been generated and built")
def test_ml_target_remains_d7_any_payment_response() -> None:
    dataset = build_d7_recovery_dataset(DATA_ROOT)
    loan_status = pd.read_parquet(DATA_ROOT / "dws" / "dws_loan_status_snapshot_di.parquet")
    expected = loan_status[["loan_id", "repaid_amount_d7"]].copy()
    expected["expected_target"] = (expected["repaid_amount_d7"].fillna(0) > 0).astype(int)
    checked = dataset[["loan_id", "is_recovered_d7"]].merge(expected[["loan_id", "expected_target"]], on="loan_id")

    assert checked["is_recovered_d7"].equals(checked["expected_target"])
    assert "is_cured" not in dataset.columns
    assert "cure_target" not in dataset.columns
