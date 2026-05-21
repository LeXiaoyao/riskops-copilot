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


def compute_feature_diagnostics(
    feature_importance: pd.DataFrame,
    top_n: int = 10,
    raw_feature_columns: list[str] | None = None,
) -> dict[str, Any]:
    top_features = feature_importance.head(top_n).copy()
    top_features["base_feature"] = [
        _base_feature_name(feature, raw_feature_columns or []) for feature in top_features["feature"].astype(str)
    ]
    vintage_rows = top_features[top_features["base_feature"] == "vintage_month"]
    total_importance = float(top_features["importance"].sum())
    vintage_importance = float(vintage_rows["importance"].sum())
    top_feature_count = int(len(top_features))
    vintage_top_feature_count = int(len(vintage_rows))
    vintage_top_feature_share = vintage_top_feature_count / top_feature_count if top_feature_count else 0.0
    vintage_top_importance_share = vintage_importance / total_importance if total_importance else 0.0
    artifact_warning = vintage_top_feature_share >= 0.3 or vintage_top_importance_share >= 0.3
    return {
        "top_n": top_n,
        "top_feature_count": top_feature_count,
        "vintage_top_feature_count": vintage_top_feature_count,
        "vintage_top_feature_share": round(vintage_top_feature_share, 6),
        "vintage_top_importance": round(vintage_importance, 6),
        "top_importance_total": round(total_importance, 6),
        "vintage_top_importance_share": round(vintage_top_importance_share, 6),
        "vintage_month_artifact_warning": artifact_warning,
        "interpretation": (
            "vintage_month dominates top features and may reflect synthetic batch/time artifact"
            if artifact_warning
            else "vintage_month is present but does not dominate top features"
        ),
    }


def _base_feature_name(transformed_feature: str, raw_feature_columns: list[str]) -> str:
    feature = transformed_feature.split("__", 1)[1] if "__" in transformed_feature else transformed_feature
    for raw_feature in sorted(raw_feature_columns, key=len, reverse=True):
        if feature == raw_feature or feature.startswith(f"{raw_feature}_"):
            return raw_feature
    return feature


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


def write_robustness_outputs(output_dir: str | Path, robustness_payload: dict[str, Any], report_markdown: str) -> dict[str, str]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    json_path = path / "robustness_check.json"
    report_path = path / "robustness_check.md"

    json_path.write_text(json.dumps(robustness_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(report_markdown, encoding="utf-8")
    return {
        "robustness_check": str(json_path),
        "robustness_report": str(report_path),
    }


def build_vintage_robustness_payload(with_vintage: dict[str, Any], without_vintage: dict[str, Any]) -> dict[str, Any]:
    with_metrics = with_vintage["metrics"]
    without_metrics = without_vintage["metrics"]
    return {
        "check_name": "vintage_month_robustness",
        "with_vintage": _robustness_run_summary(with_vintage),
        "without_vintage": _robustness_run_summary(without_vintage),
        "delta_auc": round(without_metrics["auc"] - with_metrics["auc"], 6),
        "delta_ks": round(without_metrics["ks"] - with_metrics["ks"], 6),
        "delta_pr_auc": round(without_metrics["pr_auc"] - with_metrics["pr_auc"], 6),
        "interpretation": _vintage_robustness_interpretation(with_metrics, without_metrics, with_vintage, without_vintage),
    }


def _robustness_run_summary(run_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_model": run_result["best_model"],
        "metrics": run_result["metrics"],
        "dataset_summary": run_result["dataset_summary"],
        "model_comparison": run_result["model_comparison"],
        "feature_diagnostics_by_model": run_result["feature_diagnostics_by_model"],
        "top_features": run_result["top_feature_importance"][:10],
    }


def _vintage_robustness_interpretation(
    with_metrics: dict[str, Any],
    without_metrics: dict[str, Any],
    with_vintage: dict[str, Any],
    without_vintage: dict[str, Any],
) -> str:
    auc_delta = without_metrics["auc"] - with_metrics["auc"]
    with_warning = any(
        diagnostics["vintage_month_artifact_warning"]
        for diagnostics in with_vintage["feature_diagnostics_by_model"].values()
    )
    without_top_features = {
        _base_feature_name(row["feature"], without_vintage["feature_columns"])
        for row in without_vintage["top_feature_importance"][:10]
    }
    if with_warning and abs(auc_delta) <= 0.01 and "vintage_month" not in without_top_features:
        return (
            "vintage_month shows artifact risk in at least one with-vintage model, but removing it leaves performance close; "
            "the synthetic data signal is weak and the baseline should be presented as a diagnostic demo."
        )
    if with_warning and auc_delta < -0.01:
        return (
            "performance drops after excluding vintage_month, suggesting the baseline was materially relying on synthetic "
            "batch/time signal."
        )
    return "excluding vintage_month does not reveal a material dependency on the time batch feature."


def render_robustness_report(robustness_payload: dict[str, Any]) -> str:
    with_vintage = robustness_payload["with_vintage"]
    without_vintage = robustness_payload["without_vintage"]
    lines = [
        "# M6-D3 Vintage Robustness Check",
        "",
        "## Purpose",
        "",
        "- This check compares the same offline baseline with and without `vintage_month`.",
        "- `vintage_month` is a synthetic batch/time artifact risk because it can encode calendar-generation differences.",
        "- If not excluded, the model may learn batch differences instead of stable business behavior.",
        "- This is for interview demonstration: it shows how to identify leakage-like pseudo-signal before overclaiming model quality.",
        "",
        "## Synthetic Data Boundary",
        "",
        "- Inputs are synthetic offline demo data only.",
        "- No real customer data is read.",
        "- No LLM, Agent, automated collection action, deployment, tag or release is involved.",
        "",
        "## With Vintage Metrics",
        "",
        f"- **best_model**：{with_vintage['best_model']}",
        f"- **AUC**：{with_vintage['metrics']['auc']:.6f}",
        f"- **KS**：{with_vintage['metrics']['ks']:.6f}",
        f"- **PR-AUC**：{with_vintage['metrics']['pr_auc']:.6f}",
        "",
        "## Without Vintage Metrics",
        "",
        f"- **best_model**：{without_vintage['best_model']}",
        f"- **AUC**：{without_vintage['metrics']['auc']:.6f}",
        f"- **KS**：{without_vintage['metrics']['ks']:.6f}",
        f"- **PR-AUC**：{without_vintage['metrics']['pr_auc']:.6f}",
        "",
        "## Metric Deltas",
        "",
        f"- **delta_auc**：{robustness_payload['delta_auc']:.6f}",
        f"- **delta_ks**：{robustness_payload['delta_ks']:.6f}",
        f"- **delta_pr_auc**：{robustness_payload['delta_pr_auc']:.6f}",
        "",
        "## Top Features Before",
        "",
    ]
    for row in with_vintage["top_features"]:
        lines.append(f"- **{row['feature']}**：importance={row['importance']:.6f}")
    lines.extend(["", "## Top Features After", ""])
    for row in without_vintage["top_features"]:
        lines.append(f"- **{row['feature']}**：importance={row['importance']:.6f}")
    lines.extend(
        [
            "",
            "## Artifact Warning",
            "",
            "- vintage_month remains a synthetic batch/time artifact risk even when the best model is only weakly affected.",
            "- If excluding vintage_month leaves metrics close, the right conclusion is not that the model is strong; it is that current synthetic data has weak stable signal.",
            "- If excluding vintage_month causes a large drop, the baseline is mostly using a time-batch shortcut and should not be used as business evidence.",
            "",
            "## Interpretation",
            "",
            f"- **conclusion**：{robustness_payload['interpretation']}",
            "",
            f"_Generated at {datetime.now(UTC).isoformat(timespec='seconds')}_",
            "",
        ]
    )
    return "\n".join(lines)


def render_ml_report(
    dataset_summary: dict[str, Any],
    metrics: dict[str, Any],
    lift_table: pd.DataFrame,
    feature_importance: pd.DataFrame,
    model_type: str,
    model_comparison: dict[str, Any] | None = None,
    best_model: str | None = None,
    feature_diagnostics: dict[str, Any] | None = None,
    feature_diagnostics_by_model: dict[str, Any] | None = None,
    feature_columns: list[str] | None = None,
) -> str:
    top_features = feature_importance.head(10).to_dict("records")
    model_comparison = model_comparison or {model_type: metrics}
    best_model = best_model or model_type
    feature_diagnostics = feature_diagnostics or compute_feature_diagnostics(feature_importance, raw_feature_columns=feature_columns)
    feature_diagnostics_by_model = feature_diagnostics_by_model or {model_type: feature_diagnostics}
    any_vintage_warning = any(
        diagnostics["vintage_month_artifact_warning"] for diagnostics in feature_diagnostics_by_model.values()
    )
    loan_features = "product_code, channel_code, loan_amount, loan_term, interest_rate, mob, due_amount, dpd_bucket"
    if not dataset_summary.get("exclude_vintage_month", False):
        loan_features = f"{loan_features}, vintage_month"
    lines = [
        "# M6-D2 D7 Recovery Baseline Diagnostics",
        "",
        "## Demo Disclaimer",
        "",
        "- synthetic data only",
        "- no real customer data",
        "- no real model deployment",
        "- no automated decisioning",
        "- no collection automation",
        "- no real financial conclusion",
        "- synthetic data boundary: all inputs are generated offline demo data under `synthetic_data/`",
        "",
        "## Dataset Summary",
        "",
        f"- **sample_count**：{dataset_summary['sample_count']}",
        f"- **positive_rate**：{dataset_summary['positive_rate']:.4%}",
        f"- **feature_count**：{dataset_summary['feature_count']}",
        f"- **exclude_vintage_month**：{dataset_summary.get('exclude_vintage_month', False)}",
        "- **grain**：loan_id / 借据级",
        "",
        "## Target Definition",
        "",
        "- **target**：is_recovered_d7",
        "- **definition**：1 if dws_loan_status_snapshot_di.repaid_amount_d7 > 0 else 0",
        "- **evaluation-only fields**：repaid_amount_d7, recovery_rate_d7",
        "",
        "## Business Feature Groups",
        "",
        f"- **loan features**：{loan_features}",
        "- **customer synthetic profile features**：age_group, gender, province, city, occupation_type, customer_segment, risk_level_current",
        "- **postloan score features**：postloan_c_score, score_level",
        "- **assignment context features**：initial_dpd_bucket, initial_outstanding_amount, balance_segment, current_vendor_id, current_line_id",
        "- **synthetic governance labels**：protect_flag, sensitive_flag",
        "- **recent process window features**：action_count, connected_count, ai_action_count, ptp_count, ptp_fulfilled_count, complaint_count, connect_rate, ai_coverage_rate, ptp_fulfillment_rate",
        "",
        "## Leakage Control",
        "",
        "- D7 result fields are target / evaluation only and are excluded from model features.",
        "- loan_id, customer_id, case_id and masked/hash identity columns are excluded from model features.",
        "- case features are joined through one main loan mapping per loan_id to avoid one-to-many sample inflation.",
        "- current_vendor_id and current_line_id are assignment context signals, not customer intrinsic risk factors.",
        "- protect_flag and sensitive_flag are synthetic labels, not real sensitive identity fields.",
        "- Process window features are aggregated from the recent 7-day window ending on case_create_date and do not use repayment amount/date fields.",
        "",
        "## Model Comparison",
        "",
    ]
    for comparison_model, comparison_metrics in model_comparison.items():
        lines.extend(
            [
                f"- **{comparison_model}**",
                f"  - AUC：{comparison_metrics['auc']:.6f}",
                f"  - KS：{comparison_metrics['ks']:.6f}",
                f"  - PR-AUC：{comparison_metrics['pr_auc']:.6f}",
                f"  - precision：{comparison_metrics['precision']:.6f}",
                f"  - recall：{comparison_metrics['recall']:.6f}",
                f"  - f1：{comparison_metrics['f1']:.6f}",
            ]
        )
    lines.extend(
        [
            f"- **best_model**：{best_model}",
            "",
            "## Best Model Metrics",
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
            "## Feature Diagnostics",
            "",
        ]
    )
    for diagnostics_model, diagnostics in feature_diagnostics_by_model.items():
        lines.extend(
            [
                f"- **{diagnostics_model}**",
                f"  - top_n：{diagnostics['top_n']}",
                f"  - vintage_month_top_feature_count：{diagnostics['vintage_top_feature_count']} / {diagnostics['top_feature_count']}",
                f"  - vintage_month_top_feature_share：{diagnostics['vintage_top_feature_share']:.2%}",
                f"  - vintage_month_top_importance_share：{diagnostics['vintage_top_importance_share']:.2%}",
                f"  - vintage_month_artifact_warning：{diagnostics['vintage_month_artifact_warning']}",
            ]
        )
    lines.extend(
        [
            f"- **top_n**：{feature_diagnostics['top_n']}",
            f"- **vintage_month_top_feature_count**：{feature_diagnostics['vintage_top_feature_count']} / {feature_diagnostics['top_feature_count']}",
            f"- **vintage_month_top_feature_share**：{feature_diagnostics['vintage_top_feature_share']:.2%}",
            f"- **vintage_month_top_importance_share**：{feature_diagnostics['vintage_top_importance_share']:.2%}",
            f"- **vintage_month_artifact_warning**：{any_vintage_warning}",
            f"- **interpretation**：{_vintage_warning_interpretation(any_vintage_warning)}",
            "",
            "## Vintage Month Artifact Warning",
            "",
            "- vintage_month is useful for demo diagnostics because it exposes whether synthetic calendar batches are driving separation.",
            "- vintage_month should not be the final business explanation core; it may reflect batch/time artifact rather than customer or operation behavior.",
            "- If vintage_month dominates top features, explain it as a synthetic-data diagnostic finding, not as a deployable policy reason.",
            "",
            "## Decile Lift Table",
            "",
        ]
    )
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
            "## Why Baseline AUC Is Modest",
            "",
            "- The data is synthetic and optimized for workflow demonstration, not for strong predictive signal.",
            "- The D7 target is a broad recovery outcome, while many available signals are assignment or process context rather than direct willingness-to-pay features.",
            "- Recent process features are useful for interview storytelling, but their observation window should be tightened before any production-like interpretation.",
            "- vintage_month concentration indicates possible synthetic batch effects, so business interpretation should emphasize diagnostics rather than overclaiming predictive power.",
            "",
            "## Business Interpretation",
            "",
            "- This baseline ranks synthetic loans by probability of D7 recovery and is suitable for offline model-readiness demonstration only.",
            "- Higher-ranked deciles should show higher observed recovery rate if the baseline has usable separation.",
            "- Assignment and process features can help explain operational patterns, but they should not be interpreted as customer intrinsic risk attributes.",
            "",
            "## Known Limitations",
            "",
            "- Synthetic data can validate pipeline feasibility, not real-world predictive power.",
            "- The model is not calibrated for production decisioning.",
            "- Missing postloan scores are imputed by the preprocessing pipeline.",
            "- Process features use a demo-friendly 7-day window ending on case_create_date; if upstream timing is not strict, they should be treated as diagnostic-only.",
            "- No real customer data, LLM context, collection automation or deployment path is involved.",
            "",
            "## Next Steps",
            "",
            "- Add time-based validation once the synthetic calendar design supports a stricter observation cutoff.",
            "- Add segment-level diagnostics for score_level, dpd_bucket, vendor and line stability.",
            "- Consider removing or bucketing vintage_month in a later robustness check if artifact dominance remains high.",
            "",
            f"_Generated at {datetime.now(UTC).isoformat(timespec='seconds')}_",
            "",
        ]
    )
    return "\n".join(lines)


def _vintage_warning_interpretation(any_vintage_warning: bool) -> str:
    if any_vintage_warning:
        return "at least one model shows vintage_month dominance and may reflect synthetic batch/time artifact"
    return "vintage_month is present but does not dominate top features"
