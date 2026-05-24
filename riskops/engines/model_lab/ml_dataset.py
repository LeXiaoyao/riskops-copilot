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


def load_ml_sources(base_dir: str | Path) -> dict[str, pd.DataFrame]:
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
    return sources


def build_d7_recovery_dataset(base_dir: str | Path, exclude_vintage_month: bool = False) -> pd.DataFrame:
    sources = load_ml_sources(base_dir)
    loan_status = sources["loan_status"].copy()
    loan_status["observation_date"] = pd.to_datetime(loan_status["stat_date"]).dt.normalize()
    loan_status["is_recovered_d7"] = (loan_status["repaid_amount_d7"].fillna(0) > 0).astype(int)

    dataset = loan_status[["loan_id", "customer_id", "product_code", "dpd_bucket", "due_amount", "observation_date", "is_recovered_d7"]].copy()
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

    feature_columns = get_feature_columns(dataset, exclude_vintage_month=exclude_vintage_month)
    dataset = dataset[["loan_id", "observation_date", "is_recovered_d7", *feature_columns]].copy()
    dataset.attrs["metadata"] = {
        "sample_count": int(len(dataset)),
        "positive_rate": float(dataset["is_recovered_d7"].mean()),
        "feature_count": len(feature_columns),
        "exclude_vintage_month": exclude_vintage_month,
        "excluded_time_features": get_time_batch_feature_columns() if exclude_vintage_month else [],
        "target_column": "is_recovered_d7",
        "target_semantic_name": "d7_any_payment_response",
        "target_definition": "1 if repaid_amount_d7 > 0 else 0",
        "target_boundary": "Legacy demo target name; positive means any D7 payment response, not full cure, DPD cleared, or complete recovery.",
        **score_metadata,
    }
    return dataset


def split_features_target(dataset: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    metadata = dataset.attrs.get("metadata", {})
    feature_columns = get_feature_columns(dataset, exclude_vintage_month=bool(metadata.get("exclude_vintage_month", False)))
    return dataset[feature_columns].copy(), dataset["is_recovered_d7"].astype(int).copy()


def get_feature_columns(dataset: pd.DataFrame, exclude_vintage_month: bool = False) -> list[str]:
    blocked = set(get_leakage_columns()) | set(get_sensitive_columns()) | {"is_recovered_d7"}
    if exclude_vintage_month:
        blocked.update(get_time_batch_feature_columns())
    return [column for column in FEATURE_COLUMNS if column in dataset.columns and column not in blocked]


def get_leakage_columns() -> list[str]:
    return list(LEAKAGE_COLUMNS)


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
