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
    build_decile_lift_table,
    compute_classification_metrics,
    compute_feature_diagnostics,
    render_ml_report,
    write_ml_outputs,
)

DEFAULT_DATA_DIR = ROOT / "synthetic_data"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "model_lab" / "ml_baseline"
DEFAULT_RANDOM_SEED = 20260521
DEFAULT_TEST_SIZE = 0.25


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M6-D2 D7 recovery prediction ML baseline diagnostics.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", choices=["logistic", "random_forest", "both"], default="both")
    parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE)
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        dataset = build_d7_recovery_dataset(args.data_dir)
        X, y = split_features_target(dataset)
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=args.test_size,
            random_state=args.random_seed,
            stratify=y,
        )
        model_names = ["logistic", "random_forest"] if args.model == "both" else [args.model]
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
        classification_metrics = metrics_by_model[best_model]
        lift_table = build_decile_lift_table(y_test, scores_by_model[best_model])
        feature_importance = feature_importance_by_model[best_model]
        feature_diagnostics_by_model = {
            model_name: compute_feature_diagnostics(importance, raw_feature_columns=list(X.columns))
            for model_name, importance in feature_importance_by_model.items()
        }
        feature_diagnostics = feature_diagnostics_by_model[best_model]
        summary = dataset_metadata(dataset)
        metrics_payload = {
            "model_type": best_model,
            "requested_model": args.model,
            "best_model": best_model,
            "random_seed": args.random_seed,
            "test_size": args.test_size,
            "dataset_summary": summary,
            "metrics": classification_metrics,
            "model_comparison": metrics_by_model,
            "feature_diagnostics": feature_diagnostics,
            "feature_diagnostics_by_model": feature_diagnostics_by_model,
            "top_feature_importance": feature_importance.head(10).to_dict("records"),
        }
        report = render_ml_report(
            summary,
            classification_metrics,
            lift_table,
            feature_importance,
            best_model,
            model_comparison=metrics_by_model,
            best_model=best_model,
            feature_diagnostics=feature_diagnostics,
            feature_diagnostics_by_model=feature_diagnostics_by_model,
            feature_columns=list(X.columns),
        )
        output_paths = write_ml_outputs(args.output_dir, metrics_payload, lift_table, feature_importance, report)
    except Exception as exc:
        print("FAIL ML baseline")
        print(f"ERROR {exc}")
        return 1

    print(f"sample count: {summary['sample_count']}")
    print(f"positive rate: {summary['positive_rate']:.6f}")
    print(f"feature count: {summary['feature_count']}")
    print(f"requested model: {args.model}")
    for model_name, model_metrics in metrics_by_model.items():
        print(
            f"{model_name}: AUC={model_metrics['auc']:.6f}, KS={model_metrics['ks']:.6f}, PR-AUC={model_metrics['pr_auc']:.6f}"
        )
    print(f"best model: {best_model}")
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
