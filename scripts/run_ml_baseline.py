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
    render_ml_report,
    write_ml_outputs,
)

DEFAULT_DATA_DIR = ROOT / "synthetic_data"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "model_lab" / "ml_baseline"
DEFAULT_RANDOM_SEED = 20260521
DEFAULT_TEST_SIZE = 0.25


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M6-D1 D7 recovery prediction ML baseline.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", choices=["logistic", "random_forest"], default="logistic")
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
        if args.model == "logistic":
            model = train_logistic_baseline(X_train, y_train)
        else:
            model = train_random_forest_baseline(X_train, y_train)

        scores = predict_scores(model, X_test)
        classification_metrics = compute_classification_metrics(y_test, scores)
        lift_table = build_decile_lift_table(y_test, scores)
        feature_importance = extract_feature_importance(model, list(X.columns))
        summary = dataset_metadata(dataset)
        metrics_payload = {
            "model_type": args.model,
            "random_seed": args.random_seed,
            "test_size": args.test_size,
            "dataset_summary": summary,
            "metrics": classification_metrics,
            "top_feature_importance": feature_importance.head(10).to_dict("records"),
        }
        report = render_ml_report(summary, classification_metrics, lift_table, feature_importance, args.model)
        output_paths = write_ml_outputs(args.output_dir, metrics_payload, lift_table, feature_importance, report)
    except Exception as exc:
        print("FAIL ML baseline")
        print(f"ERROR {exc}")
        return 1

    print(f"sample count: {summary['sample_count']}")
    print(f"positive rate: {summary['positive_rate']:.6f}")
    print(f"feature count: {summary['feature_count']}")
    print(f"model type: {args.model}")
    print(f"AUC: {classification_metrics['auc']:.6f}")
    print(f"KS: {classification_metrics['ks']:.6f}")
    print(f"PR-AUC: {classification_metrics['pr_auc']:.6f}")
    print("output paths:")
    for label, path in output_paths.items():
        print(f"- {label}: {path}")
    print("PASS ML baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
