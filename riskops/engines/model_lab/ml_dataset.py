"""Dataset builder for M6-D1 D7 recovery baseline modeling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "product_code",
    "channel_code",
    "loan_amount",
    "loan_term",
    "interest_rate",
    "mob",
    "vintage_month",
    "due_amount",
    "log_due_amount",
    "days_since_due_date",
    "dpd_x_log_due_amount",
    "dpd_bucket",
    "dpd_at_observation",
    "outstanding_at_observation",
    "loan_status_at_observation",
    "case_outstanding_at_observation",
    "case_dpd_bucket_at_observation",
    "case_status_at_observation",
    "customer_max_dpd_at_observation",
    "customer_total_outstanding_at_observation",
    "customer_active_case_count_at_observation",
    "age_group",
    "gender",
    "province",
    "city",
    "occupation_type",
    "customer_segment",
    "risk_level_current",
    "postloan_c_score",
    "score_x_connect_rate",
    "score_level",
    "initial_dpd_bucket",
    "initial_outstanding_amount",
    "outstanding_to_loan_ratio",
    "balance_segment",
    "protect_flag",
    "sensitive_flag",
    "current_vendor_id",
    "current_line_id",
    "action_count_7d",
    "connected_count_7d",
    "connect_rate_7d",
    "ptp_count_7d",
    "ptp_rate_7d",
    "days_since_last_action",
    "ai_action_count",
    "complaint_count",
    "ai_coverage_rate",
]

TIME_BATCH_FEATURE_COLUMNS = [
    "vintage_month",
    "first_due_date",
    "observation_date",
    "stat_date",
    "due_date",
    "case_create_date",
    "case_create_time",
]

LEAKAGE_COLUMNS = [
    "repaid_amount_d7",
    "recovery_rate_d7",
    "outstanding_at_d7",
    "outstanding_reduction_d7",
    "outstanding_reduction_rate_d7",
    "dpd_at_d7",
    "dpd_reduction_d7",
    "loan_status_at_d7",
    "case_outstanding_at_d7",
    "case_dpd_bucket_at_d7",
    "case_status_at_d7",
    "customer_total_outstanding_at_d7",
    "customer_max_dpd_at_d7",
    "customer_active_case_count_at_d7",
    "d7_end_date",
    "loan_state_d7_available",
    "repay_amount",
    "repay_date",
    "repay_time",
    "loan_status",
    "case_status",
    "ptp_fulfilled_flag",
    "ptp_fulfilled_count",
    "ptp_fulfillment_rate",
    "reduction_recovery_rate",
]

TARGET_COLUMNS = [
    "is_recovered_d7",
    "is_any_payment_d7",
    "is_cured_d7",
    "is_state_recovered_d7",
    "is_fully_recovered_d7",
    "case_cured_d7",
]

SENSITIVE_COLUMNS = [
    "customer_id_hash",
    "mobile_masked",
    "customer_id",
    "loan_id",
    "case_id",
    "id_card",
    "phone_no",
    "customer_name",
]


def load_ml_sources(base_dir: str | Path, include_state_sources: bool = False) -> dict[str, pd.DataFrame]:
    root = Path(base_dir)
    sources = {
        "loan_status": _read_parquet(root / "dws" / "dws_loan_status_snapshot_di.parquet"),
        "repayment_plan": _read_parquet(root / "ods" / "ods_repayment_plan.parquet"),
        "loan": _read_parquet(root / "dim" / "dim_loan.parquet"),
        "customer": _read_parquet(root / "dim" / "dim_customer.parquet"),
        "case_loan_mapping": _read_parquet(root / "dim" / "dim_case_loan_mapping.parquet"),
        "case": _read_parquet(root / "dim" / "dim_case.parquet"),
        "postloan_c_score": _read_parquet(root / "ods" / "ods_postloan_c_score.parquet"),
        "collection_process": _read_parquet(root / "dws" / "dws_collection_process_wide_di.parquet"),
        "collection_action": _read_parquet(root / "ods" / "ods_collection_action.parquet"),
    }
    if include_state_sources:
        sources.update(
            {
                "loan_daily_snapshot": _read_parquet(root / "ods" / "ods_loan_daily_snapshot.parquet"),
                "case_daily_snapshot": _read_parquet(root / "ods" / "ods_case_daily_snapshot.parquet"),
                "customer_daily_snapshot": _read_parquet(root / "ods" / "ods_customer_daily_snapshot.parquet"),
            }
        )
    return sources


def build_d7_recovery_dataset(
    base_dir: str | Path,
    exclude_vintage_month: bool = False,
    target: str = "any_payment",
) -> pd.DataFrame:
    if target not in {"any_payment", "state_recovery"}:
        raise ValueError(f"unsupported target: {target}")
    sources = load_ml_sources(base_dir, include_state_sources=target == "state_recovery")
    loan_status = sources["loan_status"].copy()
    loan_status["observation_date"] = pd.to_datetime(loan_status["stat_date"]).dt.normalize()
    loan_status["is_recovered_d7"] = (loan_status["repaid_amount_d7"].fillna(0) > 0).astype(int)
    loan_status["is_any_payment_d7"] = loan_status["is_recovered_d7"]

    dataset = loan_status[
        [
            "loan_id",
            "customer_id",
            "product_code",
            "dpd_bucket",
            "due_amount",
            "observation_date",
            "repaid_amount_d7",
            "recovery_rate_d7",
            "is_recovered_d7",
            "is_any_payment_d7",
        ]
    ].copy()
    state_metadata = {}
    if target == "state_recovery":
        state_targets, state_metadata = _d7_state_recovery_targets(
            dataset[["loan_id", "customer_id", "observation_date", "repaid_amount_d7"]],
            sources,
        )
        dataset = dataset.merge(state_targets, on=["loan_id", "customer_id", "observation_date"], how="left", validate="one_to_one")
    dataset["log_due_amount"] = _safe_log1p(dataset["due_amount"])

    due_dates = _loan_due_dates(sources["repayment_plan"])
    dataset = dataset.merge(due_dates, on="loan_id", how="left", validate="many_to_one")
    dataset["days_since_due_date"] = _days_between(dataset["observation_date"], dataset["due_date"])
    dataset["dpd_x_log_due_amount"] = dataset["days_since_due_date"] * dataset["log_due_amount"]

    loan = sources["loan"].drop(columns=["product_code"], errors="ignore")
    dataset = dataset.merge(
        loan[
            [
                "loan_id",
                "channel_code",
                "loan_amount",
                "loan_term",
                "interest_rate",
                "mob",
                "vintage_month",
            ]
        ],
        on="loan_id",
        how="left",
        validate="one_to_one",
    )

    customer = sources["customer"][
        [
            "customer_id",
            "gender",
            "age_group",
            "province",
            "city",
            "occupation_type",
            "customer_segment",
            "risk_level_current",
        ]
    ]
    dataset = dataset.merge(customer, on="customer_id", how="left", validate="many_to_one")

    score, score_metadata = _score_by_customer_asof_observation(
        dataset[["loan_id", "customer_id", "observation_date"]],
        sources["postloan_c_score"],
    )
    dataset = dataset.merge(score, on="loan_id", how="left", validate="one_to_one")

    case_features = _loan_level_case_features(
        sources["case_loan_mapping"],
        sources["case"],
        sources["collection_process"],
    )
    dataset = dataset.merge(case_features, on="loan_id", how="left", validate="one_to_one")
    action_features = _recent_action_features_by_loan(
        dataset[["loan_id", "observation_date"]],
        sources["case_loan_mapping"],
        sources["collection_action"],
    )
    dataset = dataset.merge(action_features, on="loan_id", how="left", validate="one_to_one")
    dataset["score_x_connect_rate"] = _safe_score_connect_interaction(dataset["postloan_c_score"], dataset["connect_rate_7d"])
    dataset["outstanding_to_loan_ratio"] = _safe_rate(dataset["initial_outstanding_amount"], dataset["loan_amount"])
    for boolean_column in ["protect_flag", "sensitive_flag"]:
        if boolean_column in dataset.columns:
            dataset[boolean_column] = dataset[boolean_column].map({True: 1.0, False: 0.0})
    count_columns = [
        "action_count_7d",
        "connected_count_7d",
        "ai_action_count",
        "ptp_count_7d",
        "ptp_fulfilled_count",
        "complaint_count",
    ]
    rate_columns = ["connect_rate_7d", "ptp_rate_7d", "ai_coverage_rate", "ptp_fulfillment_rate"]
    for process_column in [*count_columns, *rate_columns]:
        if process_column in dataset.columns:
            dataset[process_column] = dataset[process_column].fillna(0.0)

    target_column = "is_recovered_d7" if target == "any_payment" else "is_state_recovered_d7"
    if target == "state_recovery":
        dataset = dataset[dataset["loan_state_observation_available"] & dataset["loan_state_d7_available"]].copy()
    for column in TARGET_COLUMNS:
        if column in dataset.columns:
            dataset[column] = dataset[column].fillna(0).astype(int)
    feature_columns = get_feature_columns(dataset, exclude_vintage_month=exclude_vintage_month)
    outcome_columns = [column for column in get_outcome_columns() if target == "state_recovery" and column in dataset.columns]
    dataset = dataset[["loan_id", "observation_date", target_column, *outcome_columns, *feature_columns]].copy()
    dataset = dataset.loc[:, ~dataset.columns.duplicated()].copy()
    dataset.attrs["metadata"] = {
        "sample_count": int(len(dataset)),
        "positive_rate": float(dataset[target_column].mean()),
        "feature_count": len(feature_columns),
        "exclude_vintage_month": exclude_vintage_month,
        "excluded_time_features": get_time_batch_feature_columns() if exclude_vintage_month else [],
        "target": target,
        "target_column": target_column,
        **_target_metadata(target, dataset),
        **state_metadata,
        **score_metadata,
    }
    return dataset


def split_features_target(dataset: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    metadata = dataset.attrs.get("metadata", {})
    feature_columns = get_feature_columns(dataset, exclude_vintage_month=bool(metadata.get("exclude_vintage_month", False)))
    target_column = metadata.get("target_column", "is_recovered_d7")
    return dataset[feature_columns].copy(), dataset[target_column].astype(int).copy()


def get_feature_columns(dataset: pd.DataFrame, exclude_vintage_month: bool = False) -> list[str]:
    blocked = set(get_leakage_columns()) | set(get_sensitive_columns()) | set(TARGET_COLUMNS)
    if exclude_vintage_month:
        blocked.update(get_time_batch_feature_columns())
    return [column for column in FEATURE_COLUMNS if column in dataset.columns and column not in blocked]


def get_leakage_columns() -> list[str]:
    return list(LEAKAGE_COLUMNS)


def get_outcome_columns() -> list[str]:
    return list(dict.fromkeys([*LEAKAGE_COLUMNS, *TARGET_COLUMNS]))


def get_sensitive_columns() -> list[str]:
    return list(SENSITIVE_COLUMNS)


def get_time_batch_feature_columns() -> list[str]:
    return list(TIME_BATCH_FEATURE_COLUMNS)


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"ML source table not found: {path}")
    return pd.read_parquet(path)


def _score_by_customer_asof_observation(
    loan_observation: pd.DataFrame,
    score: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    columns = ["loan_id", "postloan_c_score", "score_level"]
    if loan_observation.empty or score.empty:
        return (
            pd.DataFrame(columns=columns),
            {
                "score_date_guard": "latest_score_on_or_before_observation_date_with_missing_impute_fallback",
                "score_date_fallback_count": int(len(loan_observation)),
                "score_date_missing_count": int(len(loan_observation)),
                "future_score_blocked_count": 0,
                "score_date_fallback_strategy": "missing_impute",
            },
        )

    base = loan_observation[["loan_id", "customer_id", "observation_date"]].copy()
    base["observation_date"] = pd.to_datetime(base["observation_date"]).dt.normalize()
    score_frame = score[["customer_id", "score_date", "postloan_c_score", "score_level"]].copy()
    score_frame["score_date"] = pd.to_datetime(score_frame["score_date"]).dt.normalize()
    candidates = base.merge(score_frame, on="customer_id", how="left")

    future_score_blocked_count = int(
        candidates[candidates["score_date"] > candidates["observation_date"]]["loan_id"].nunique()
    )

    historical = candidates[candidates["score_date"] <= candidates["observation_date"]].copy()
    historical = historical.sort_values(["loan_id", "score_date"]).drop_duplicates("loan_id", keep="last")
    historical = historical[columns]

    fallback_loan_ids = base.loc[~base["loan_id"].isin(historical["loan_id"]), "loan_id"]
    result = base[["loan_id"]].merge(historical, on="loan_id", how="left", validate="one_to_one")
    fallback_count = int(len(fallback_loan_ids))
    missing_count = int(result["postloan_c_score"].isna().sum())
    metadata = {
        "score_date_guard": "latest_score_on_or_before_observation_date_with_missing_impute_fallback",
        "score_date_fallback_count": fallback_count,
        "score_date_missing_count": missing_count,
        "future_score_blocked_count": future_score_blocked_count,
        "score_date_fallback_strategy": "missing_impute",
    }
    return result[columns], metadata


def _loan_due_dates(repayment_plan: pd.DataFrame) -> pd.DataFrame:
    if repayment_plan.empty:
        return pd.DataFrame(columns=["loan_id", "due_date"])
    due_dates = repayment_plan[["loan_id", "due_date"]].copy()
    due_dates["due_date"] = pd.to_datetime(due_dates["due_date"]).dt.normalize()
    return due_dates.sort_values(["loan_id", "due_date"]).drop_duplicates("loan_id", keep="first")


def _safe_log1p(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").clip(lower=0)
    result = pd.Series(np.log1p(numeric), index=values.index)
    return result.replace([np.inf, -np.inf], np.nan)


def _days_between(end_date: pd.Series, start_date: pd.Series) -> pd.Series:
    days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).dt.days
    return days.clip(lower=0).fillna(0).astype(float)


def _target_metadata(target: str, dataset: pd.DataFrame) -> dict[str, Any]:
    if target == "state_recovery":
        return {
            "target_column": "is_state_recovered_d7",
            "target_semantic_name": "d7_state_recovery_proxy",
            "target_definition": (
                "1 if D7 end dpd is 0, outstanding decreases from observation to D7, "
                "and repaid_amount_d7 > 0 else 0"
            ),
            "target_boundary": (
                "This is a D7 state recovery proxy. Strict cure-to-current requires dpd_at_observation > 0; "
                "current synthetic daily snapshot coverage yields zero strict cure positives, so the trainable "
                "baseline uses state recovery rather than claiming full cure."
            ),
            "evaluation_only_fields": [
                "repaid_amount_d7",
                "recovery_rate_d7",
                "outstanding_at_d7",
                "outstanding_reduction_d7",
                "outstanding_reduction_rate_d7",
                "dpd_at_d7",
                "dpd_reduction_d7",
                "loan_status_at_d7",
                "case_status_at_d7",
                "customer_total_outstanding_at_d7",
                "customer_max_dpd_at_d7",
                "is_cured_d7",
                "is_state_recovered_d7",
                "is_fully_recovered_d7",
            ],
            "strict_cure_positive_rate": float(dataset["is_cured_d7"].mean()) if "is_cured_d7" in dataset else 0.0,
            "state_recovery_positive_rate": float(dataset["is_state_recovered_d7"].mean())
            if "is_state_recovered_d7" in dataset
            else 0.0,
            "full_recovery_positive_rate": float(dataset["is_fully_recovered_d7"].mean())
            if "is_fully_recovered_d7" in dataset
            else 0.0,
        }
    return {
        "target_column": "is_recovered_d7",
        "target_semantic_name": "d7_any_payment_response",
        "target_definition": "1 if repaid_amount_d7 > 0 else 0",
        "target_boundary": (
            "Legacy demo target name; positive means any D7 payment response, not full cure, "
            "DPD cleared, or complete recovery."
        ),
        "evaluation_only_fields": ["repaid_amount_d7", "recovery_rate_d7"],
        "any_payment_positive_rate": float(dataset["is_recovered_d7"].mean()) if "is_recovered_d7" in dataset else 0.0,
    }


def _d7_state_recovery_targets(loan_observation: pd.DataFrame, sources: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, Any]]:
    base = loan_observation.copy()
    base["observation_date"] = pd.to_datetime(base["observation_date"]).dt.normalize()
    base["d7_end_date"] = base["observation_date"] + pd.Timedelta(days=7)

    loan_obs = _loan_snapshot_asof(base, sources["loan_daily_snapshot"], "observation_date", "observation")
    loan_d7 = _loan_snapshot_asof(base, sources["loan_daily_snapshot"], "d7_end_date", "d7")
    result = base.merge(loan_obs, on=["loan_id", "observation_date"], how="left").merge(
        loan_d7, on=["loan_id", "d7_end_date"], how="left"
    )

    case_state = _case_state_targets(base, sources["case_loan_mapping"], sources["case_daily_snapshot"])
    result = result.merge(case_state, on=["loan_id", "observation_date", "d7_end_date"], how="left")
    customer_state = _customer_state_targets(base, sources["customer_daily_snapshot"])
    result = result.merge(customer_state, on=["customer_id", "observation_date", "d7_end_date"], how="left")

    result["loan_state_observation_available"] = result["dpd_at_observation"].notna()
    result["loan_state_d7_available"] = result["dpd_at_d7"].notna()
    result["outstanding_reduction_d7"] = (
        pd.to_numeric(result["outstanding_at_observation"], errors="coerce")
        - pd.to_numeric(result["outstanding_at_d7"], errors="coerce")
    ).clip(lower=0)
    result["outstanding_reduction_rate_d7"] = _safe_rate(
        result["outstanding_reduction_d7"],
        pd.to_numeric(result["outstanding_at_observation"], errors="coerce"),
    )
    result["dpd_reduction_d7"] = (
        pd.to_numeric(result["dpd_at_observation"], errors="coerce") - pd.to_numeric(result["dpd_at_d7"], errors="coerce")
    ).clip(lower=0)
    result["is_cured_d7"] = (
        (pd.to_numeric(result["dpd_at_observation"], errors="coerce") > 0)
        & (pd.to_numeric(result["dpd_at_d7"], errors="coerce") == 0)
        & (result["outstanding_reduction_d7"] > 0)
    ).astype(int)
    result["is_state_recovered_d7"] = (
        (pd.to_numeric(result["dpd_at_d7"], errors="coerce") == 0)
        & (result["outstanding_reduction_d7"] > 0)
        & (pd.to_numeric(result["repaid_amount_d7"], errors="coerce").fillna(0) > 0)
    ).astype(int)
    result["is_fully_recovered_d7"] = (
        (pd.to_numeric(result["outstanding_at_observation"], errors="coerce") > 0)
        & (pd.to_numeric(result["outstanding_at_d7"], errors="coerce") <= 0.01)
    ).astype(int)

    result["case_cured_d7"] = (
        result["case_status_at_d7"].isin(["cured", "closed"])
        | (pd.to_numeric(result["case_outstanding_at_d7"], errors="coerce") <= 0.01)
    ).fillna(False).astype(int)
    metadata = _state_snapshot_metadata(result)
    columns = [
        "loan_id",
        "customer_id",
        "observation_date",
        "d7_end_date",
        "loan_state_observation_available",
        "loan_state_d7_available",
        "outstanding_at_observation",
        "outstanding_at_d7",
        "outstanding_reduction_d7",
        "outstanding_reduction_rate_d7",
        "dpd_at_observation",
        "dpd_at_d7",
        "dpd_reduction_d7",
        "loan_status_at_observation",
        "loan_status_at_d7",
        "case_cured_d7",
        "case_outstanding_at_observation",
        "case_outstanding_at_d7",
        "case_dpd_bucket_at_observation",
        "case_dpd_bucket_at_d7",
        "case_status_at_observation",
        "case_status_at_d7",
        "customer_max_dpd_at_observation",
        "customer_max_dpd_at_d7",
        "customer_total_outstanding_at_observation",
        "customer_total_outstanding_at_d7",
        "customer_active_case_count_at_observation",
        "customer_active_case_count_at_d7",
        "is_cured_d7",
        "is_state_recovered_d7",
        "is_fully_recovered_d7",
    ]
    return result[columns], metadata


def _loan_snapshot_asof(base: pd.DataFrame, loan_snapshot: pd.DataFrame, anchor_column: str, suffix: str) -> pd.DataFrame:
    snapshot = loan_snapshot[["loan_id", "stat_date", "dpd", "dpd_bucket", "outstanding_amount", "loan_status"]].copy()
    snapshot["stat_date"] = pd.to_datetime(snapshot["stat_date"]).dt.normalize()
    joined = base[["loan_id", anchor_column]].merge(snapshot, on="loan_id", how="left")
    joined = joined[joined["stat_date"] <= joined[anchor_column]].copy()
    joined = joined.sort_values(["loan_id", anchor_column, "stat_date"]).drop_duplicates(["loan_id", anchor_column], keep="last")
    return joined.rename(
        columns={
            "stat_date": f"snapshot_date_{suffix}",
            "dpd": f"dpd_at_{suffix}",
            "dpd_bucket": f"dpd_bucket_at_{suffix}",
            "outstanding_amount": f"outstanding_at_{suffix}",
            "loan_status": f"loan_status_at_{suffix}",
        }
    )[["loan_id", anchor_column, f"snapshot_date_{suffix}", f"dpd_at_{suffix}", f"dpd_bucket_at_{suffix}", f"outstanding_at_{suffix}", f"loan_status_at_{suffix}"]]


def _case_state_targets(base: pd.DataFrame, mapping: pd.DataFrame, case_snapshot: pd.DataFrame) -> pd.DataFrame:
    main_mapping = mapping[mapping["main_loan_flag"].fillna(False)].copy()
    main_mapping = main_mapping.sort_values(["loan_id", "mapping_start_date"]).drop_duplicates("loan_id", keep="last")
    case_base = base[["loan_id", "observation_date", "d7_end_date"]].merge(
        main_mapping[["loan_id", "case_id"]], on="loan_id", how="left", validate="one_to_one"
    )
    case_obs = _case_snapshot_asof(case_base, case_snapshot, "observation_date", "observation")
    case_d7 = _case_snapshot_asof(case_base, case_snapshot, "d7_end_date", "d7")
    return case_base[["loan_id", "observation_date", "d7_end_date"]].merge(
        case_obs, on=["loan_id", "observation_date"], how="left"
    ).merge(case_d7, on=["loan_id", "d7_end_date"], how="left")


def _case_snapshot_asof(case_base: pd.DataFrame, case_snapshot: pd.DataFrame, anchor_column: str, suffix: str) -> pd.DataFrame:
    snapshot = case_snapshot[["case_id", "stat_date", "dpd_bucket", "outstanding_amount", "case_status"]].copy()
    snapshot["stat_date"] = pd.to_datetime(snapshot["stat_date"]).dt.normalize()
    joined = case_base[["loan_id", "case_id", anchor_column]].merge(snapshot, on="case_id", how="left")
    joined = joined[joined["stat_date"] <= joined[anchor_column]].copy()
    joined = joined.sort_values(["loan_id", anchor_column, "stat_date"]).drop_duplicates(["loan_id", anchor_column], keep="last")
    return joined.rename(
        columns={
            "stat_date": f"case_snapshot_date_{suffix}",
            "dpd_bucket": f"case_dpd_bucket_at_{suffix}",
            "outstanding_amount": f"case_outstanding_at_{suffix}",
            "case_status": f"case_status_at_{suffix}",
        }
    )[["loan_id", anchor_column, f"case_outstanding_at_{suffix}", f"case_dpd_bucket_at_{suffix}", f"case_status_at_{suffix}"]]


def _customer_state_targets(base: pd.DataFrame, customer_snapshot: pd.DataFrame) -> pd.DataFrame:
    customer_base = base[["customer_id", "observation_date", "d7_end_date"]].drop_duplicates().copy()
    customer_obs = _customer_snapshot_asof(customer_base, customer_snapshot, "observation_date", "observation")
    customer_d7 = _customer_snapshot_asof(customer_base, customer_snapshot, "d7_end_date", "d7")
    return customer_base.merge(
        customer_obs, on=["customer_id", "observation_date"], how="left"
    ).merge(customer_d7, on=["customer_id", "d7_end_date"], how="left")


def _customer_snapshot_asof(base: pd.DataFrame, customer_snapshot: pd.DataFrame, anchor_column: str, suffix: str) -> pd.DataFrame:
    snapshot = customer_snapshot[
        ["customer_id", "stat_date", "max_dpd", "total_outstanding_amount", "active_case_count", "risk_level"]
    ].copy()
    snapshot["stat_date"] = pd.to_datetime(snapshot["stat_date"]).dt.normalize()
    joined = base[["customer_id", anchor_column]].merge(snapshot, on="customer_id", how="left")
    joined = joined[joined["stat_date"] <= joined[anchor_column]].copy()
    joined = joined.sort_values(["customer_id", anchor_column, "stat_date"]).drop_duplicates(
        ["customer_id", anchor_column], keep="last"
    )
    return joined.rename(
        columns={
            "stat_date": f"customer_snapshot_date_{suffix}",
            "max_dpd": f"customer_max_dpd_at_{suffix}",
            "total_outstanding_amount": f"customer_total_outstanding_at_{suffix}",
            "active_case_count": f"customer_active_case_count_at_{suffix}",
            "risk_level": f"customer_risk_level_at_{suffix}",
        }
    )[
        [
            "customer_id",
            anchor_column,
            f"customer_max_dpd_at_{suffix}",
            f"customer_total_outstanding_at_{suffix}",
            f"customer_active_case_count_at_{suffix}",
        ]
    ]


def _state_snapshot_metadata(result: pd.DataFrame) -> dict[str, Any]:
    complete = result["loan_state_observation_available"] & result["loan_state_d7_available"]
    return {
        "d7_state_snapshot_strategy": "latest_snapshot_on_or_before_anchor_date",
        "d7_state_complete_count": int(complete.sum()),
        "d7_state_missing_count": int((~complete).sum()),
        "loan_observation_snapshot_match_count": int(result["loan_state_observation_available"].sum()),
        "loan_d7_snapshot_match_count": int(result["loan_state_d7_available"].sum()),
        "loan_observation_exact_snapshot_count": int((result["snapshot_date_observation"] == result["observation_date"]).sum()),
        "loan_d7_exact_snapshot_count": int((result["snapshot_date_d7"] == result["d7_end_date"]).sum()),
    }


def _safe_score_connect_interaction(score: pd.Series, connect_rate: pd.Series) -> pd.Series:
    score_proxy = pd.to_numeric(score, errors="coerce") / 100.0
    rate = pd.to_numeric(connect_rate, errors="coerce").fillna(0.0)
    result = score_proxy * rate
    return result.replace([np.inf, -np.inf], np.nan)


def _recent_action_features_by_loan(
    loan_observation: pd.DataFrame,
    mapping: pd.DataFrame,
    action: pd.DataFrame,
    window_days: int = 7,
) -> pd.DataFrame:
    columns = [
        "loan_id",
        "action_count_7d",
        "connected_count_7d",
        "connect_rate_7d",
        "ptp_count_7d",
        "ptp_rate_7d",
        "days_since_last_action",
    ]
    if loan_observation.empty or mapping.empty or action.empty:
        return pd.DataFrame(columns=columns)

    main_mapping = mapping[mapping["main_loan_flag"].fillna(False)].copy()
    main_mapping = main_mapping.sort_values(["loan_id", "mapping_start_date"]).drop_duplicates("loan_id", keep="last")
    base = loan_observation.merge(main_mapping[["loan_id", "case_id"]], on="loan_id", how="left", validate="one_to_one")
    base["observation_date"] = pd.to_datetime(base["observation_date"]).dt.normalize()

    action_frame = action[["case_id", "action_time", "connected_flag", "ptp_flag"]].copy()
    action_frame["action_date"] = pd.to_datetime(action_frame["action_time"]).dt.normalize()
    joined = action_frame.merge(base[["loan_id", "case_id", "observation_date"]], on="case_id", how="inner")
    historical = joined[joined["action_date"] <= joined["observation_date"]].copy()
    last_action = historical.groupby("loan_id")["action_date"].max().rename("last_action_date")

    lower_bound = joined["observation_date"] - pd.to_timedelta(window_days - 1, unit="D")
    window = joined[(joined["action_date"] >= lower_bound) & (joined["action_date"] <= joined["observation_date"])].copy()
    if window.empty:
        result = base[["loan_id"]].drop_duplicates().copy()
        for column in ["action_count_7d", "connected_count_7d", "connect_rate_7d", "ptp_count_7d", "ptp_rate_7d"]:
            result[column] = 0.0
    else:
        aggregated = (
            window.groupby("loan_id", as_index=False)
            .agg(
                action_count_7d=("case_id", "count"),
                connected_count_7d=("connected_flag", "sum"),
                ptp_count_7d=("ptp_flag", "sum"),
            )
        )
        aggregated["connect_rate_7d"] = _safe_rate(aggregated["connected_count_7d"], aggregated["action_count_7d"])
        aggregated["ptp_rate_7d"] = _safe_rate(aggregated["ptp_count_7d"], aggregated["action_count_7d"])
        result = base[["loan_id"]].drop_duplicates().merge(aggregated, on="loan_id", how="left")
        for column in ["action_count_7d", "connected_count_7d", "connect_rate_7d", "ptp_count_7d", "ptp_rate_7d"]:
            result[column] = result[column].fillna(0.0)

    result = result.merge(last_action, on="loan_id", how="left")
    result = result.merge(base[["loan_id", "observation_date"]], on="loan_id", how="left", validate="one_to_one")
    result["days_since_last_action"] = _days_between(result["observation_date"], result["last_action_date"])
    result.loc[result["last_action_date"].isna(), "days_since_last_action"] = np.nan
    return result[columns]


def _loan_level_case_features(mapping: pd.DataFrame, case: pd.DataFrame, collection_process: pd.DataFrame) -> pd.DataFrame:
    main_mapping = mapping[mapping["main_loan_flag"].fillna(False)].copy()
    main_mapping = main_mapping.sort_values(["loan_id", "mapping_start_date"]).drop_duplicates("loan_id", keep="last")
    case_columns = [
        "case_id",
        "case_create_time",
        "initial_dpd_bucket",
        "initial_outstanding_amount",
        "balance_segment",
        "protect_flag",
        "sensitive_flag",
        "current_vendor_id",
        "current_line_id",
    ]
    case_features = main_mapping[["loan_id", "case_id"]].merge(
        case[case_columns],
        on="case_id",
        how="left",
        validate="many_to_one",
    )
    process_features = _recent_collection_process_features(case_features, collection_process)
    case_features = case_features.merge(process_features, on="loan_id", how="left", validate="one_to_one")
    return case_features.drop(columns=["case_id", "case_create_time"])


def _recent_collection_process_features(case_features: pd.DataFrame, collection_process: pd.DataFrame, window_days: int = 7) -> pd.DataFrame:
    process_columns = [
        "action_count",
        "connected_count",
        "ai_action_count",
        "ptp_count",
        "ptp_fulfilled_count",
        "complaint_count",
    ]
    if collection_process.empty or case_features.empty:
        return pd.DataFrame(columns=["loan_id", *process_columns, "connect_rate", "ai_coverage_rate", "ptp_fulfillment_rate"])

    window_base = case_features[["loan_id", "case_id", "case_create_time"]].copy()
    window_base["observation_date"] = pd.to_datetime(window_base["case_create_time"]).dt.normalize()

    process = collection_process[["stat_date", "case_id", *process_columns]].copy()
    process["stat_date"] = pd.to_datetime(process["stat_date"]).dt.normalize()
    process = process.merge(window_base[["loan_id", "case_id", "observation_date"]], on="case_id", how="inner")
    lower_bound = process["observation_date"] - pd.to_timedelta(window_days - 1, unit="D")
    process = process[(process["stat_date"] >= lower_bound) & (process["stat_date"] <= process["observation_date"])]
    if process.empty:
        return pd.DataFrame(columns=["loan_id", *process_columns, "connect_rate", "ai_coverage_rate", "ptp_fulfillment_rate"])

    aggregated = process.groupby("loan_id", as_index=False)[process_columns].sum()
    aggregated["connect_rate"] = _safe_rate(aggregated["connected_count"], aggregated["action_count"])
    aggregated["ai_coverage_rate"] = _safe_rate(aggregated["ai_action_count"], aggregated["action_count"])
    aggregated["ptp_fulfillment_rate"] = _safe_rate(aggregated["ptp_fulfilled_count"], aggregated["ptp_count"])
    return aggregated


def _safe_rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    rate = numerator.divide(denominator.where(denominator != 0))
    return rate.fillna(0.0)


def dataset_metadata(dataset: pd.DataFrame) -> dict[str, Any]:
    metadata = dict(dataset.attrs.get("metadata", {}))
    metadata.setdefault("sample_count", int(len(dataset)))
    metadata.setdefault("positive_rate", float(dataset["is_recovered_d7"].mean()))
    metadata.setdefault(
        "feature_count",
        len(get_feature_columns(dataset, exclude_vintage_month=bool(metadata.get("exclude_vintage_month", False)))),
    )
    metadata.setdefault("exclude_vintage_month", False)
    metadata.setdefault("excluded_time_features", [])
    return metadata
