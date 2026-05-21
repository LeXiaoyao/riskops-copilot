from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from riskops.engines.model_lab.baseline_model import predict_scores, train_logistic_baseline
from riskops.engines.model_lab.ml_dataset import (
    build_d7_recovery_dataset,
    get_feature_columns,
    get_leakage_columns,
    get_sensitive_columns,
    split_features_target,
)
from riskops.engines.model_lab.ml_metrics import (
    build_decile_lift_table,
    compute_classification_metrics,
    render_ml_report,
    write_ml_outputs,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "synthetic_data"
RUNNER = ROOT / "scripts" / "run_ml_baseline.py"


def test_can_build_d7_recovery_dataset() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)

    assert len(dataset) == 30000
    assert dataset.attrs["metadata"]["sample_count"] == 30000


def test_target_exists_and_has_both_classes() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)

    assert "is_recovered_d7" in dataset.columns
    assert set(dataset["is_recovered_d7"].unique()) == {0, 1}


def test_sensitive_fields_do_not_enter_features() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    feature_columns = set(get_feature_columns(dataset))

    assert feature_columns.isdisjoint(get_sensitive_columns())


def test_leakage_fields_do_not_enter_features() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    feature_columns = set(get_feature_columns(dataset))

    assert feature_columns.isdisjoint(get_leakage_columns())


def test_model_can_train_and_output_scores() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, _ = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)

    model = train_logistic_baseline(X_train, y_train)
    scores = predict_scores(model, X_test)

    assert len(scores) == len(X_test)
    assert scores.min() >= 0
    assert scores.max() <= 1


def test_metrics_include_auc_ks_pr_auc() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)
    model = train_logistic_baseline(X_train, y_train)
    scores = predict_scores(model, X_test)

    metrics = compute_classification_metrics(y_test, scores)

    assert {"auc", "ks", "pr_auc"} <= set(metrics)
    assert 0 <= metrics["auc"] <= 1
    assert 0 <= metrics["ks"] <= 1
    assert 0 <= metrics["pr_auc"] <= 1


def test_lift_table_can_generate() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)
    model = train_logistic_baseline(X_train, y_train)
    scores = predict_scores(model, X_test)

    lift_table = build_decile_lift_table(y_test, scores)

    assert len(lift_table) == 10
    assert {"decile", "lift", "cumulative_capture_rate"} <= set(lift_table.columns)


def test_report_can_generate(tmp_path: Path) -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)
    model = train_logistic_baseline(X_train, y_train)
    scores = predict_scores(model, X_test)
    metrics = compute_classification_metrics(y_test, scores)
    lift_table = build_decile_lift_table(y_test, scores)
    feature_importance = model.named_steps["preprocess"].get_feature_names_out()
    feature_importance_frame = pd.DataFrame(
        {"feature": feature_importance, "importance": range(len(feature_importance)), "signed_weight": range(len(feature_importance))}
    )
    report = render_ml_report(dataset.attrs["metadata"], metrics, lift_table, feature_importance_frame, "logistic")
    paths = write_ml_outputs(tmp_path, {"metrics": metrics}, lift_table, feature_importance_frame, report)

    assert Path(paths["report"]).exists()
    assert "M6-D1 D7 Recovery Prediction Baseline" in Path(paths["report"]).read_text(encoding="utf-8")


def test_cli_can_run(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--data-dir",
            str(DATA_DIR),
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS ML baseline" in result.stdout
    assert (tmp_path / "model_metrics.json").exists()


def test_cli_report_contains_required_disclaimers(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--data-dir",
            str(DATA_DIR),
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = (tmp_path / "ml_baseline_report.md").read_text(encoding="utf-8")
    assert "synthetic data" in report
    assert "no real customer data" in report
    assert "no automated decisioning" in report


def test_cli_metrics_json_contains_dataset_summary(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--data-dir",
            str(DATA_DIR),
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads((tmp_path / "model_metrics.json").read_text(encoding="utf-8"))
    assert payload["dataset_summary"]["sample_count"] == 30000
    assert payload["dataset_summary"]["feature_count"] > 0
