"""Run M6-D1 D7 recovery prediction baseline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.model_lab.baseline_model import (
    extract_feature_importance,
    predict_scores,
    train_logistic_baseline,
    train_random_forest_baseline,
)
from riskops.engines.model_lab.ml_dataset import build_d7_recovery_dataset, dataset_metadata, split_features_target
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

DEFAULT_DATA_DIR = ROOT / "synthetic_data"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "model_lab" / "ml_baseline"
DEFAULT_RANDOM_SEED = 20260521
DEFAULT_TEST_SIZE = 0.25


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M6-D2 D7 recovery prediction ML baseline diagnostics.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--target", choices=["any_payment", "state_recovery"], default="any_payment")
    parser.add_argument("--model", choices=["logistic", "random_forest", "both"], default="both")
    parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE)
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--exclude-vintage-month", action="store_true")
    return parser


def _run_baseline(
    data_dir: Path,
    target: str,
    model_choice: str,
    test_size: float,
    random_seed: int,
    exclude_vintage_month: bool,
) -> dict[str, object]:
    dataset = build_d7_recovery_dataset(data_dir, exclude_vintage_month=exclude_vintage_month, target=target)
    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_seed,
        stratify=y,
    )
    model_names = ["logistic", "random_forest"] if model_choice == "both" else [model_choice]
    metrics_by_model = {}
    scores_by_model = {}
    feature_importance_by_model = {}
    for model_name in model_names:
        if model_name == "logistic":
            model = train_logistic_baseline(X_train, y_train)
        else:
            model = train_random_forest_baseline(X_train, y_train)
        scores = predict_scores(model, X_test)
        scores_by_model[model_name] = scores
        metrics_by_model[model_name] = compute_classification_metrics(y_test, scores)
        feature_importance_by_model[model_name] = extract_feature_importance(model, list(X.columns))

    best_model = max(
        metrics_by_model,
        key=lambda name: (metrics_by_model[name]["auc"], metrics_by_model[name]["pr_auc"], metrics_by_model[name]["ks"]),
    )
    feature_importance = feature_importance_by_model[best_model]
    feature_diagnostics_by_model = {
        model_name: compute_feature_diagnostics(importance, raw_feature_columns=list(X.columns))
        for model_name, importance in feature_importance_by_model.items()
    }
    summary = dataset_metadata(dataset)
    return {
        "model_type": best_model,
        "requested_model": model_choice,
        "best_model": best_model,
        "random_seed": random_seed,
        "test_size": test_size,
        "exclude_vintage_month": exclude_vintage_month,
        "target": target,
        "dataset_summary": summary,
        "metrics": metrics_by_model[best_model],
        "model_comparison": metrics_by_model,
        "feature_diagnostics": feature_diagnostics_by_model[best_model],
        "feature_diagnostics_by_model": feature_diagnostics_by_model,
        "top_feature_importance": feature_importance.head(10).to_dict("records"),
        "feature_columns": list(X.columns),
        "lift_table": build_decile_lift_table(y_test, scores_by_model[best_model]),
        "feature_importance": feature_importance,
    }


def _write_selected_outputs(output_dir: Path, result: dict[str, object]) -> dict[str, str]:
    report = render_ml_report(
        result["dataset_summary"],
        result["metrics"],
        result["lift_table"],
        result["feature_importance"],
        result["best_model"],
        model_comparison=result["model_comparison"],
        best_model=result["best_model"],
        feature_diagnostics=result["feature_diagnostics"],
        feature_diagnostics_by_model=result["feature_diagnostics_by_model"],
        feature_columns=result["feature_columns"],
    )
    summary = result["dataset_summary"]
    metrics = result["metrics"]
    lift_table = result["lift_table"]
    top_decile = lift_table.iloc[0].to_dict() if len(lift_table) else {}
    metrics_payload = {
        key: value
        for key, value in result.items()
        if key not in {"lift_table", "feature_importance", "feature_columns"}
    }
    metrics_payload.update(
        {
            "row_count": summary["sample_count"],
            "positive_rate": summary["positive_rate"],
            "train_test_split": {
                "method": "stratified_random_split",
                "test_size": result["test_size"],
                "random_seed": result["random_seed"],
            },
            "auc": metrics["auc"],
            "ks": metrics["ks"],
            "pr_auc": metrics["pr_auc"],
            "lift": float(top_decile.get("lift", 0.0)),
            "top_decile_capture_rate": float(top_decile.get("cumulative_capture_rate", 0.0)),
            "leakage_guard_summary": {
                "pii_features_blocked": True,
                "outcome_features_blocked": True,
                "score_date_guard": summary.get("score_date_guard", "not_recorded"),
                "future_score_blocked_count": summary.get("future_score_blocked_count", 0),
                "target_boundary": summary.get("target_boundary", ""),
            },
            "caveats": [
                "synthetic data validates pipeline feasibility, not real-world predictive power",
                "baseline is not calibrated for production decisioning",
                "D7 any-payment response is not a cure-to-current label",
                "vintage_month may reflect synthetic batch/time artifacts",
            ],
        }
    )
    return write_ml_outputs(output_dir, metrics_payload, result["lift_table"], result["feature_importance"], report)


def _write_robustness_outputs(output_dir: Path, with_vintage: dict[str, object], without_vintage: dict[str, object]) -> dict[str, str]:
    robustness_payload = build_vintage_robustness_payload(with_vintage, without_vintage)
    robustness_report = render_robustness_report(robustness_payload)
    return write_robustness_outputs(output_dir, robustness_payload, robustness_report)


def _state_target_positive_count(dataset) -> int:
    target_column = dataset.attrs.get("metadata", {}).get("target_column", "is_state_recovered_d7")
    return int(dataset[target_column].sum()) if target_column in dataset.columns else 0


def _build_state_recovery_feasibility_summary(dataset) -> dict[str, object]:
    metadata = dataset.attrs.get("metadata", {})
    target_column = metadata.get("target_column", "is_state_recovered_d7")
    return {
        "target": metadata.get("target", "state_recovery"),
        "target_column": target_column,
        "sample_count": int(len(dataset)),
        "positive_count": _state_target_positive_count(dataset),
        "positive_rate": float(dataset[target_column].mean()) if target_column in dataset.columns and len(dataset) else 0.0,
        "strict_cure_positive_count": int(dataset["is_cured_d7"].sum()) if "is_cured_d7" in dataset.columns else 0,
        "state_recovery_positive_count": int(dataset["is_state_recovered_d7"].sum())
        if "is_state_recovered_d7" in dataset.columns
        else 0,
        "full_recovery_positive_count": int(dataset["is_fully_recovered_d7"].sum())
        if "is_fully_recovered_d7" in dataset.columns
        else 0,
        "decision": "feasibility_only_skip_training",
        "snapshot_strategy": metadata.get("d7_state_snapshot_strategy"),
        "d7_state_complete_count": metadata.get("d7_state_complete_count"),
        "d7_state_missing_count": metadata.get("d7_state_missing_count"),
    }


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.target == "state_recovery":
            feasibility_dataset = build_d7_recovery_dataset(
                args.data_dir,
                exclude_vintage_month=args.exclude_vintage_month,
                target=args.target,
            )
            summary = _build_state_recovery_feasibility_summary(feasibility_dataset)
            print(f"sample count: {summary['sample_count']}")
            print(f"target: {summary['target']}")
            print(f"target column: {summary['target_column']}")
            print(f"positive rate: {summary['positive_rate']:.6f}")
            print(f"positive count: {summary['positive_count']}")
            print(f"strict cure positive count: {summary['strict_cure_positive_count']}")
            print(f"state recovery positive count: {summary['state_recovery_positive_count']}")
            print(f"full recovery positive count: {summary['full_recovery_positive_count']}")
            print(f"d7 state complete count: {summary['d7_state_complete_count']}")
            print(f"d7 state missing count: {summary['d7_state_missing_count']}")
            print("training skipped: state_recovery is feasibility-only")
            print("output paths: none")
            print("PASS ML target feasibility")
            return 0
        selected_result = _run_baseline(
            args.data_dir,
            args.target,
            args.model,
            args.test_size,
            args.random_seed,
            exclude_vintage_month=args.exclude_vintage_month,
        )
        with_vintage_result = (
            _run_baseline(
                args.data_dir,
                args.target,
                args.model,
                args.test_size,
                args.random_seed,
                exclude_vintage_month=False,
            )
            if args.exclude_vintage_month
            else selected_result
        )
        without_vintage_result = (
            selected_result
            if args.exclude_vintage_month
            else _run_baseline(
                args.data_dir,
                args.target,
                args.model,
                args.test_size,
                args.random_seed,
                exclude_vintage_month=True,
            )
        )
        output_paths = _write_selected_outputs(args.output_dir, selected_result)
        robustness_paths = _write_robustness_outputs(args.output_dir, with_vintage_result, without_vintage_result)
        output_paths.update(robustness_paths)
    except Exception as exc:
        print("FAIL ML baseline")
        print(f"ERROR {exc}")
        return 1

    summary = selected_result["dataset_summary"]
    metrics_by_model = selected_result["model_comparison"]
    classification_metrics = selected_result["metrics"]
    feature_diagnostics_by_model = selected_result["feature_diagnostics_by_model"]
    print(f"sample count: {summary['sample_count']}")
    print(f"target: {args.target}")
    print(f"target column: {summary['target_column']}")
    print(f"positive rate: {summary['positive_rate']:.6f}")
    print(f"feature count: {summary['feature_count']}")
    print(f"requested model: {args.model}")
    print(f"exclude vintage month: {args.exclude_vintage_month}")
    for model_name, model_metrics in metrics_by_model.items():
        print(
            f"{model_name}: AUC={model_metrics['auc']:.6f}, KS={model_metrics['ks']:.6f}, PR-AUC={model_metrics['pr_auc']:.6f}"
        )
    print(f"best model: {selected_result['best_model']}")
    print(f"AUC: {classification_metrics['auc']:.6f}")
    print(f"KS: {classification_metrics['ks']:.6f}")
    print(f"PR-AUC: {classification_metrics['pr_auc']:.6f}")
    for model_name, diagnostics in feature_diagnostics_by_model.items():
        print(
            f"{model_name} vintage top feature share: {diagnostics['vintage_top_feature_share']:.6f}, "
            f"artifact warning: {diagnostics['vintage_month_artifact_warning']}"
        )
    print("output paths:")
    for label, path in output_paths.items():
        print(f"- {label}: {path}")
    print("PASS ML baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
