"""Sklearn baseline models for M6-D1 recovery prediction."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def train_logistic_baseline(X_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    preprocessor = _build_preprocessor(X_train)
    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=20260521)
    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )
    pipeline.fit(X_train, y_train)
    return pipeline


def train_random_forest_baseline(X_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    preprocessor = _build_preprocessor(X_train)
    model = RandomForestClassifier(
        n_estimators=120,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=20260521,
        n_jobs=-1,
    )
    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )
    pipeline.fit(X_train, y_train)
    return pipeline


def predict_scores(model: Pipeline, X_test: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X_test)[:, 1]
    if hasattr(model, "decision_function"):
        raw_scores = model.decision_function(X_test)
        return 1.0 / (1.0 + np.exp(-raw_scores))
    raise TypeError("Model must expose predict_proba or decision_function.")


def extract_feature_importance(model: Pipeline, feature_names: list[str]) -> pd.DataFrame:
    del feature_names
    transformed_names = list(model.named_steps["preprocess"].get_feature_names_out())
    estimator = model.named_steps["model"]
    if hasattr(estimator, "coef_"):
        signed_weight = estimator.coef_[0]
        importance = np.abs(signed_weight)
    elif hasattr(estimator, "feature_importances_"):
        importance = estimator.feature_importances_
        signed_weight = importance
    else:
        importance = np.zeros(len(transformed_names))
        signed_weight = np.zeros(len(transformed_names))

    frame = pd.DataFrame(
        {
            "feature": transformed_names,
            "importance": importance,
            "signed_weight": signed_weight,
        }
    )
    return frame.sort_values(["importance", "feature"], ascending=[False, True]).reset_index(drop=True)


def _build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_columns = list(X.select_dtypes(include=["number", "bool"]).columns)
    categorical_columns = [column for column in X.columns if column not in numeric_columns]
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_columns),
            ("cat", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
    )
