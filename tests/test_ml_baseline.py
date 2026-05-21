from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from riskops.engines.model_lab.baseline_model import predict_scores, train_logistic_baseline, train_random_forest_baseline
from riskops.engines.model_lab.ml_dataset import (
    build_d7_recovery_dataset,
    get_feature_columns,
    get_leakage_columns,
    get_sensitive_columns,
    get_time_batch_feature_columns,
    split_features_target,
)
from riskops.engines.model_lab.ml_metrics import (
    build_vintage_robustness_payload,
    build_decile_lift_table,
    compute_classification_metrics,
    compute_feature_diagnostics,
    render_ml_report,
    render_robustness_report,
    write_ml_outputs,
    write_robustness_outputs,
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


def test_exclude_vintage_month_removes_time_batch_features() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR, exclude_vintage_month=True)
    feature_columns = set(get_feature_columns(dataset, exclude_vintage_month=True))

    assert "vintage_month" not in feature_columns
    assert feature_columns.isdisjoint(get_time_batch_feature_columns())
    assert dataset.attrs["metadata"]["exclude_vintage_month"] is True


def test_business_features_exist_or_are_safely_skipped() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    feature_columns = set(get_feature_columns(dataset))
    expected_features = {
        "postloan_c_score",
        "score_level",
        "initial_dpd_bucket",
        "initial_outstanding_amount",
        "balance_segment",
        "current_vendor_id",
        "current_line_id",
        "protect_flag",
        "sensitive_flag",
        "action_count",
        "connected_count",
        "ai_action_count",
        "ptp_count",
        "ptp_fulfilled_count",
        "complaint_count",
        "connect_rate",
        "ai_coverage_rate",
        "ptp_fulfillment_rate",
    }

    assert expected_features <= feature_columns
    assert dataset[["action_count", "connected_count", "ai_action_count", "ptp_count"]].min().min() >= 0


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


def test_model_comparison_metrics_can_generate() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)
    models = {
        "logistic": train_logistic_baseline(X_train, y_train),
        "random_forest": train_random_forest_baseline(X_train, y_train),
    }
    comparison = {
        model_name: compute_classification_metrics(y_test, predict_scores(model, X_test))
        for model_name, model in models.items()
    }

    assert {"logistic", "random_forest"} <= set(comparison)
    assert all(0 <= metrics["auc"] <= 1 for metrics in comparison.values())


def test_lift_table_can_generate() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)
    model = train_logistic_baseline(X_train, y_train)
    scores = predict_scores(model, X_test)

    lift_table = build_decile_lift_table(y_test, scores)

    assert len(lift_table) == 10
    assert {"decile", "lift", "cumulative_capture_rate"} <= set(lift_table.columns)


def test_feature_diagnostics_can_generate() -> None:
    dataset = build_d7_recovery_dataset(DATA_DIR)
    X, y = split_features_target(dataset)
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.25, random_state=20260521, stratify=y)
    model = train_logistic_baseline(X_train, y_train)
    feature_importance = pd.DataFrame(
        {
            "feature": model.named_steps["preprocess"].get_feature_names_out(),
            "importance": range(len(model.named_steps["preprocess"].get_feature_names_out())),
            "signed_weight": range(len(model.named_steps["preprocess"].get_feature_names_out())),
        }
    )

    diagnostics = compute_feature_diagnostics(feature_importance, raw_feature_columns=list(X.columns))

    assert {"vintage_top_feature_share", "vintage_month_artifact_warning"} <= set(diagnostics)


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
    diagnostics = compute_feature_diagnostics(feature_importance_frame, raw_feature_columns=list(X.columns))
    report = render_ml_report(
        dataset.attrs["metadata"],
        metrics,
        lift_table,
        feature_importance_frame,
        "logistic",
        model_comparison={"logistic": metrics},
        best_model="logistic",
        feature_diagnostics=diagnostics,
        feature_columns=list(X.columns),
    )
    paths = write_ml_outputs(tmp_path, {"metrics": metrics}, lift_table, feature_importance_frame, report)

    assert Path(paths["report"]).exists()
    report_text = Path(paths["report"]).read_text(encoding="utf-8")
    assert "M6-D2 D7 Recovery Baseline Diagnostics" in report_text
    assert "Vintage Month Artifact Warning" in report_text
    assert "synthetic data boundary" in report_text


def test_cli_can_run(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--data-dir",
            str(DATA_DIR),
            "--output-dir",
            str(tmp_path),
            "--model",
            "both",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS ML baseline" in result.stdout
    assert (tmp_path / "model_metrics.json").exists()
    assert (tmp_path / "robustness_check.json").exists()
    assert (tmp_path / "robustness_check.md").exists()


def test_cli_can_run_without_vintage_month(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--data-dir",
            str(DATA_DIR),
            "--output-dir",
            str(tmp_path),
            "--exclude-vintage-month",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads((tmp_path / "model_metrics.json").read_text(encoding="utf-8"))
    assert payload["dataset_summary"]["exclude_vintage_month"] is True
    assert not any("vintage_month" in row["feature"] for row in payload["top_feature_importance"])


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
    robustness_report = (tmp_path / "robustness_check.md").read_text(encoding="utf-8")
    assert "synthetic batch/time artifact risk" in robustness_report
    assert "If not excluded" in robustness_report


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
    assert {"logistic", "random_forest"} <= set(payload["model_comparison"])
    assert "feature_diagnostics" in payload
    assert {"logistic", "random_forest"} <= set(payload["feature_diagnostics_by_model"])
    robustness_payload = json.loads((tmp_path / "robustness_check.json").read_text(encoding="utf-8"))
    assert {"with_vintage", "without_vintage", "delta_auc", "delta_ks", "delta_pr_auc"} <= set(robustness_payload)
    assert {"auc", "ks", "pr_auc"} <= set(robustness_payload["with_vintage"]["metrics"])
    assert {"auc", "ks", "pr_auc"} <= set(robustness_payload["without_vintage"]["metrics"])


def test_robustness_outputs_can_generate(tmp_path: Path) -> None:
    metrics = {
        "auc": 0.54,
        "ks": 0.07,
        "pr_auc": 0.30,
        "precision": 0.30,
        "recall": 0.60,
        "f1": 0.40,
        "threshold": 0.5,
        "confusion_matrix": {"tn": 1, "fp": 1, "fn": 1, "tp": 1},
    }
    with_vintage = {
        "best_model": "logistic",
        "metrics": metrics,
        "dataset_summary": {"sample_count": 10, "positive_rate": 0.3, "feature_count": 2},
        "model_comparison": {"logistic": metrics},
        "feature_diagnostics_by_model": {
            "logistic": {
                "vintage_month_artifact_warning": True,
                "top_n": 10,
                "top_feature_count": 1,
                "vintage_top_feature_count": 1,
                "vintage_top_feature_share": 1.0,
                "vintage_top_importance_share": 1.0,
            }
        },
        "top_feature_importance": [{"feature": "cat__vintage_month_2025-01", "importance": 1.0, "signed_weight": 1.0}],
        "feature_columns": ["vintage_month"],
    }
    without_vintage = {
        **with_vintage,
        "feature_diagnostics_by_model": {"logistic": {**with_vintage["feature_diagnostics_by_model"]["logistic"], "vintage_month_artifact_warning": False}},
        "top_feature_importance": [{"feature": "num__due_amount", "importance": 1.0, "signed_weight": 1.0}],
        "feature_columns": ["due_amount"],
    }

    payload = build_vintage_robustness_payload(with_vintage, without_vintage)
    report = render_robustness_report(payload)
    paths = write_robustness_outputs(tmp_path, payload, report)

    assert Path(paths["robustness_check"]).exists()
    assert Path(paths["robustness_report"]).exists()
    assert "synthetic batch/time artifact risk" in Path(paths["robustness_report"]).read_text(encoding="utf-8")
