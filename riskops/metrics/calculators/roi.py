"""Reduction ROI metric calculators."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from riskops.metrics.calculators.base import DATA_ROOT, as_date, read_table, safe_rate

ROOT = Path(__file__).resolve().parents[3]
METRIC_PARAMS_PATH = ROOT / "configs" / "metric_params.yaml"
DEFAULT_BASELINE_RECOVERY_WITHOUT_REDUCTION = 0.82


def load_metric_params(path: Path = METRIC_PARAMS_PATH) -> dict[str, float]:
    if not path.exists():
        return {"baseline_recovery_without_reduction": DEFAULT_BASELINE_RECOVERY_WITHOUT_REDUCTION}
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    roi_params = data.get("reduction_roi", data) if isinstance(data, dict) else {}
    baseline = roi_params.get("baseline_recovery_without_reduction", DEFAULT_BASELINE_RECOVERY_WITHOUT_REDUCTION)
    if not isinstance(baseline, int | float):
        raise ValueError("configs/metric_params.yaml reduction_roi.baseline_recovery_without_reduction must be numeric")
    return {"baseline_recovery_without_reduction": float(baseline)}


def _reduction_daily(root: Path = DATA_ROOT) -> pd.DataFrame:
    reduction = read_table(root, "ods", "ods_reduction_application").copy()
    reduction["stat_date"] = as_date(reduction["apply_time"])
    return reduction


def reduction_usage_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    reduction = _reduction_daily(root)
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    eligible = case_status.groupby("stat_date", as_index=False).agg(eligible_case_count=("case_id", "nunique"))
    used = reduction.groupby("stat_date", as_index=False).agg(reduction_case_count=("case_id", "nunique"))
    daily = eligible.merge(used, on="stat_date", how="left").fillna({"reduction_case_count": 0})
    daily["reduction_usage_rate"] = safe_rate(daily["reduction_case_count"], daily["eligible_case_count"]).to_numpy()
    return daily[["stat_date", "reduction_usage_rate"]]


def reduction_recovery_rate(root: Path = DATA_ROOT) -> pd.DataFrame:
    reduction = _reduction_daily(root)
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    reduced_cases = reduction[["stat_date", "case_id"]].drop_duplicates()
    joined = case_status.merge(reduced_cases, on=["stat_date", "case_id"], how="inner")
    daily = joined.groupby("stat_date", as_index=False).agg(
        repay_amount_after_reduction=("repaid_amount", "sum"),
        reduction_case_outstanding_amount=("outstanding_amount", "sum"),
    )
    daily["reduction_recovery_rate"] = safe_rate(daily["repay_amount_after_reduction"], daily["reduction_case_outstanding_amount"]).to_numpy()
    return daily[["stat_date", "reduction_recovery_rate"]]


def reduction_roi(root: Path = DATA_ROOT) -> pd.DataFrame:
    params = load_metric_params()
    reduction = _reduction_daily(root)
    case_status = read_table(root, "dws", "dws_case_status_snapshot_di").copy()
    case_status["stat_date"] = as_date(case_status["stat_date"])
    reduced_cases = reduction.groupby("stat_date", as_index=False).agg(
        approved_reduction_amount=("approved_amount", "sum"),
        reduction_case_count=("case_id", "nunique"),
    )
    repay = case_status.groupby("stat_date", as_index=False).agg(actual_repay=("repaid_amount", "sum"))
    daily = reduced_cases.merge(repay, on="stat_date", how="left").fillna({"actual_repay": 0})
    baseline = params["baseline_recovery_without_reduction"]
    daily["expected_repay_without_reduction"] = daily["actual_repay"] * baseline
    daily["reduction_roi"] = np.where(
        daily["approved_reduction_amount"] > 0,
        (daily["actual_repay"] - daily["expected_repay_without_reduction"]) / daily["approved_reduction_amount"],
        0.0,
    ).round(6)
    return daily[["stat_date", "reduction_roi"]]


ROI_METRICS = {
    "reduction_usage_rate": reduction_usage_rate,
    "reduction_recovery_rate": reduction_recovery_rate,
    "reduction_roi": reduction_roi,
}
