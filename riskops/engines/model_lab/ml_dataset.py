"""Dataset builder for M6-D1 D7 recovery baseline modeling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
    "dpd_bucket",
    "age_group",
    "gender",
    "province",
    "city",
    "occupation_type",
    "customer_segment",
    "risk_level_current",
    "postloan_c_score",
    "score_level",
    "initial_dpd_bucket",
    "initial_outstanding_amount",
    "balance_segment",
    "protect_flag",
    "sensitive_flag",
    "current_vendor_id",
    "current_line_id",
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
        "loan": _read_parquet(root / "dim" / "dim_loan.parquet"),
        "customer": _read_parquet(root / "dim" / "dim_customer.parquet"),
        "case_loan_mapping": _read_parquet(root / "dim" / "dim_case_loan_mapping.parquet"),
        "case": _read_parquet(root / "dim" / "dim_case.parquet"),
        "postloan_c_score": _read_parquet(root / "ods" / "ods_postloan_c_score.parquet"),
    }
    return sources


def build_d7_recovery_dataset(base_dir: str | Path) -> pd.DataFrame:
    sources = load_ml_sources(base_dir)
    loan_status = sources["loan_status"].copy()
    loan_status["is_recovered_d7"] = (loan_status["repaid_amount_d7"].fillna(0) > 0).astype(int)

    dataset = loan_status[["loan_id", "customer_id", "product_code", "dpd_bucket", "due_amount", "is_recovered_d7"]].copy()

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
            "sensitive_flag",
        ]
    ]
    dataset = dataset.merge(customer, on="customer_id", how="left", validate="many_to_one")

    score = _latest_score_by_customer(sources["postloan_c_score"])
    dataset = dataset.merge(score, on="customer_id", how="left", validate="many_to_one")

    case_features = _loan_level_case_features(sources["case_loan_mapping"], sources["case"])
    dataset = dataset.merge(case_features, on="loan_id", how="left", validate="one_to_one")
    for boolean_column in ["protect_flag", "sensitive_flag"]:
        if boolean_column in dataset.columns:
            dataset[boolean_column] = dataset[boolean_column].map({True: 1.0, False: 0.0})

    feature_columns = get_feature_columns(dataset)
    dataset = dataset[["loan_id", "is_recovered_d7", *feature_columns]].copy()
    dataset.attrs["metadata"] = {
        "sample_count": int(len(dataset)),
        "positive_rate": float(dataset["is_recovered_d7"].mean()),
        "feature_count": len(feature_columns),
    }
    return dataset


def split_features_target(dataset: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_columns = get_feature_columns(dataset)
    return dataset[feature_columns].copy(), dataset["is_recovered_d7"].astype(int).copy()


def get_feature_columns(dataset: pd.DataFrame) -> list[str]:
    blocked = set(get_leakage_columns()) | set(get_sensitive_columns()) | {"is_recovered_d7"}
    return [column for column in FEATURE_COLUMNS if column in dataset.columns and column not in blocked]


def get_leakage_columns() -> list[str]:
    return list(LEAKAGE_COLUMNS)


def get_sensitive_columns() -> list[str]:
    return list(SENSITIVE_COLUMNS)


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"ML source table not found: {path}")
    return pd.read_parquet(path)


def _latest_score_by_customer(score: pd.DataFrame) -> pd.DataFrame:
    if score.empty:
        return pd.DataFrame(columns=["customer_id", "postloan_c_score", "score_level"])
    latest = score.sort_values(["customer_id", "score_date"]).drop_duplicates("customer_id", keep="last")
    return latest[["customer_id", "postloan_c_score", "score_level"]].copy()


def _loan_level_case_features(mapping: pd.DataFrame, case: pd.DataFrame) -> pd.DataFrame:
    main_mapping = mapping[mapping["main_loan_flag"].fillna(False)].copy()
    main_mapping = main_mapping.sort_values(["loan_id", "mapping_start_date"]).drop_duplicates("loan_id", keep="last")
    case_columns = [
        "case_id",
        "initial_dpd_bucket",
        "initial_outstanding_amount",
        "balance_segment",
        "protect_flag",
        "current_vendor_id",
        "current_line_id",
    ]
    case_features = main_mapping[["loan_id", "case_id"]].merge(
        case[case_columns],
        on="case_id",
        how="left",
        validate="many_to_one",
    )
    return case_features.drop(columns=["case_id"])


def dataset_metadata(dataset: pd.DataFrame) -> dict[str, Any]:
    metadata = dict(dataset.attrs.get("metadata", {}))
    metadata.setdefault("sample_count", int(len(dataset)))
    metadata.setdefault("positive_rate", float(dataset["is_recovered_d7"].mean()))
    metadata.setdefault("feature_count", len(get_feature_columns(dataset)))
    return metadata
