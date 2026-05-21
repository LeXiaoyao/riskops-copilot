"""Metrics and output rendering for M6-D1 ML baseline."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def compute_auc(y_true: pd.Series | np.ndarray, y_score: np.ndarray) -> float:
    return float(roc_auc_score(y_true, y_score))


def compute_ks(y_true: pd.Series | np.ndarray, y_score: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def compute_pr_auc(y_true: pd.Series | np.ndarray, y_score: np.ndarray) -> float:
    return float(average_precision_score(y_true, y_score))


def compute_classification_metrics(y_true: pd.Series | np.ndarray, y_score: np.ndarray, threshold: float = 0.5) -> dict[str, Any]:
    y_pred = (y_score >= threshold).astype(int)
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return {
        "auc": round(compute_auc(y_true, y_score), 6),
        "ks": round(compute_ks(y_true, y_score), 6),
        "pr_auc": round(compute_pr_auc(y_true, y_score), 6),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 6),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 6),
        "threshold": threshold,
        "confusion_matrix": {
            "tn": int(matrix[0, 0]),
            "fp": int(matrix[0, 1]),
            "fn": int(matrix[1, 0]),
            "tp": int(matrix[1, 1]),
        },
    }


def build_decile_lift_table(y_true: pd.Series | np.ndarray, y_score: np.ndarray) -> pd.DataFrame:
    frame = pd.DataFrame({"y_true": np.asarray(y_true), "score": np.asarray(y_score)})
    frame = frame.sort_values("score", ascending=False).reset_index(drop=True)
    base_rate = float(frame["y_true"].mean())
    total_positive = int(frame["y_true"].sum())
    chunk_indexes = np.array_split(np.arange(len(frame)), 10)
    rows = []
    cumulative_positive = 0
    for index, chunk_index in enumerate(chunk_indexes, start=1):
        chunk = frame.iloc[chunk_index]
        positive_count = int(chunk["y_true"].sum())
        cumulative_positive += positive_count
        positive_rate = float(chunk["y_true"].mean()) if len(chunk) else 0.0
        rows.append(
            {
                "decile": index,
                "sample_count": int(len(chunk)),
                "positive_count": positive_count,
                "positive_rate": round(positive_rate, 6),
                "avg_score": round(float(chunk["score"].mean()), 6) if len(chunk) else 0.0,
                "lift": round(positive_rate / base_rate, 6) if base_rate else 0.0,
                "cumulative_positive_count": cumulative_positive,
                "cumulative_capture_rate": round(cumulative_positive / total_positive, 6) if total_positive else 0.0,
            }
        )
    return pd.DataFrame(rows)


def write_ml_outputs(
    output_dir: str | Path,
    metrics: dict[str, Any],
    lift_table: pd.DataFrame,
    feature_importance: pd.DataFrame,
    report_markdown: str,
) -> dict[str, str]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    metrics_path = path / "model_metrics.json"
    importance_path = path / "feature_importance.csv"
    lift_path = path / "lift_table.csv"
    report_path = path / "ml_baseline_report.md"

    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    feature_importance.to_csv(importance_path, index=False)
    lift_table.to_csv(lift_path, index=False)
    report_path.write_text(report_markdown, encoding="utf-8")
    return {
        "model_metrics": str(metrics_path),
        "feature_importance": str(importance_path),
        "lift_table": str(lift_path),
        "report": str(report_path),
    }


def render_ml_report(
    dataset_summary: dict[str, Any],
    metrics: dict[str, Any],
    lift_table: pd.DataFrame,
    feature_importance: pd.DataFrame,
    model_type: str,
) -> str:
    top_features = feature_importance.head(10).to_dict("records")
    lines = [
        "# M6-D1 D7 Recovery Prediction Baseline",
        "",
        "## Demo Disclaimer",
        "",
        "- synthetic data only",
        "- no real customer data",
        "- no real model deployment",
        "- no automated decisioning",
        "- no collection automation",
        "- no real financial conclusion",
        "",
        "## Dataset Summary",
        "",
        f"- **sample_count**：{dataset_summary['sample_count']}",
        f"- **positive_rate**：{dataset_summary['positive_rate']:.4%}",
        f"- **feature_count**：{dataset_summary['feature_count']}",
        "- **grain**：loan_id / 借据级",
        "",
        "## Target Definition",
        "",
        "- **target**：is_recovered_d7",
        "- **definition**：1 if dws_loan_status_snapshot_di.repaid_amount_d7 > 0 else 0",
        "- **evaluation-only fields**：repaid_amount_d7, recovery_rate_d7",
        "",
        "## Feature Groups",
        "",
        "- **loan features**：product_code, channel_code, loan_amount, loan_term, interest_rate, mob, vintage_month, due_amount, dpd_bucket",
        "- **customer synthetic profile features**：age_group, gender, province, city, occupation_type, customer_segment, risk_level_current",
        "- **postloan score features**：postloan_c_score, score_level",
        "- **assignment context features**：initial_dpd_bucket, initial_outstanding_amount, balance_segment, current_vendor_id, current_line_id",
        "- **synthetic governance labels**：protect_flag, sensitive_flag",
        "",
        "## Leakage Control",
        "",
        "- D7 result fields are target / evaluation only and are excluded from model features.",
        "- loan_id, customer_id, case_id and masked/hash identity columns are excluded from model features.",
        "- case features are joined through one main loan mapping per loan_id to avoid one-to-many sample inflation.",
        "- current_vendor_id and current_line_id are assignment context signals, not customer intrinsic risk factors.",
        "- protect_flag and sensitive_flag are synthetic labels, not real sensitive identity fields.",
        "",
        "## Model Metrics",
        "",
        f"- **model_type**：{model_type}",
        f"- **AUC**：{metrics['auc']:.6f}",
        f"- **KS**：{metrics['ks']:.6f}",
        f"- **PR-AUC**：{metrics['pr_auc']:.6f}",
        f"- **precision**：{metrics['precision']:.6f}",
        f"- **recall**：{metrics['recall']:.6f}",
        f"- **f1**：{metrics['f1']:.6f}",
        f"- **confusion_matrix**：tn={metrics['confusion_matrix']['tn']}, fp={metrics['confusion_matrix']['fp']}, fn={metrics['confusion_matrix']['fn']}, tp={metrics['confusion_matrix']['tp']}",
        "",
        "## Decile Lift Table",
        "",
    ]
    for row in lift_table.to_dict("records"):
        lines.append(
            f"- **decile {row['decile']}**：sample_count={row['sample_count']}, positive_rate={row['positive_rate']:.6f}, lift={row['lift']:.6f}, cumulative_capture_rate={row['cumulative_capture_rate']:.6f}"
        )
    lines.extend(["", "## Feature Importance", ""])
    for row in top_features:
        lines.append(f"- **{row['feature']}**：importance={row['importance']:.6f}, signed_weight={row['signed_weight']:.6f}")
    lines.extend(
        [
            "",
            "## Business Interpretation",
            "",
            "- This baseline ranks synthetic loans by probability of D7 recovery and is suitable for offline model-readiness demonstration only.",
            "- Higher-ranked deciles should show higher observed recovery rate if the baseline has usable separation.",
            "- Assignment context features can help explain operational allocation patterns, but they should not be interpreted as customer risk attributes.",
            "",
            "## Known Limitations",
            "",
            "- Synthetic data can validate pipeline feasibility, not real-world predictive power.",
            "- The model is not calibrated for production decisioning.",
            "- Missing postloan scores are imputed by the preprocessing pipeline.",
            "- No real customer data, LLM context, collection automation or deployment path is involved.",
            "",
            "## Next Steps",
            "",
            "- Add CLI integration only after M6-D1 outputs are accepted.",
            "- Add model card / validation checklist before any future production-like discussion.",
            "- Consider time-based validation in a later M6 task if the synthetic calendar design is expanded.",
            "",
            f"_Generated at {datetime.now(UTC).isoformat(timespec='seconds')}_",
            "",
        ]
    )
    return "\n".join(lines)
