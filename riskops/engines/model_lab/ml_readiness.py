"""ML readiness assessment for the synthetic M6 model lab."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from riskops.engines.model_lab.ml_dataset import (
    build_d7_recovery_dataset,
    get_feature_columns,
    get_leakage_columns,
    get_sensitive_columns,
)


def assess_ml_readiness(data_dir: str | Path) -> dict[str, Any]:
    root = Path(data_dir)
    d7_dataset = build_d7_recovery_dataset(root, target="any_payment")
    state_dataset = build_d7_recovery_dataset(root, target="state_recovery")
    action = pd.read_parquet(root / "ods" / "ods_collection_action.parquet")

    feature_columns = set(get_feature_columns(d7_dataset))
    leakage_columns = set(get_leakage_columns())
    sensitive_columns = set(get_sensitive_columns())
    ptp_rows = action[action["ptp_flag"].fillna(False)].copy()

    candidates = [
        _d7_candidate(d7_dataset),
        _state_recovery_candidate(state_dataset),
        _ptp_candidate(ptp_rows),
    ]
    recommended = next(candidate for candidate in candidates if candidate["target_id"] == "d7_any_payment_response")
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "data_boundary": "synthetic_data_only",
        "recommended_target": recommended["target_id"],
        "recommendation_reason": "cleanest available label, complete loan-level grain, usable class balance, and existing leakage guards",
        "candidates": candidates,
        "leakage_guard_summary": {
            "pii_features_blocked": feature_columns.isdisjoint(sensitive_columns),
            "outcome_features_blocked": feature_columns.isdisjoint(leakage_columns),
            "sensitive_columns_checked": sorted(sensitive_columns),
            "outcome_columns_checked": sorted(leakage_columns),
            "score_date_guard": d7_dataset.attrs["metadata"].get("score_date_guard"),
            "future_score_blocked_count": d7_dataset.attrs["metadata"].get("future_score_blocked_count", 0),
            "feature_count": len(feature_columns),
        },
        "demo_boundary": [
            "synthetic data only",
            "no real customer data",
            "no PII in model features",
            "no future D7 outcome fields in features",
            "no production model claim",
            "no automated financial or collection decisioning",
        ],
        "next_action": "run ml-baseline for the D7 any-payment response baseline and keep state_recovery as feasibility-only until stricter state labels improve",
    }


def render_ml_readiness_report(readiness: dict[str, Any]) -> str:
    lines = [
        "# M6-D ML Modeling Readiness",
        "",
        "## Conclusion",
        "",
        f"- **recommended_target**：{readiness['recommended_target']}",
        f"- **reason**：{readiness['recommendation_reason']}",
        "- **boundary**：synthetic data only; no real customer data; no PII; no automated decisioning.",
        "",
        "## Candidate Targets",
        "",
    ]
    for candidate in readiness["candidates"]:
        lines.extend(
            [
                f"### {candidate['target_id']}",
                f"- **decision**：{candidate['decision']}",
                f"- **grain**：{candidate['grain']}",
                f"- **row_count**：{candidate['row_count']}",
                f"- **positive_rate**：{candidate['positive_rate']:.6f}",
                f"- **label_source**：{candidate['label_source']}",
                f"- **leakage_risk**：{candidate['leakage_risk']}",
                f"- **notes**：{candidate['notes']}",
                "",
            ]
        )
    guard = readiness["leakage_guard_summary"]
    lines.extend(
        [
            "## Leakage Guard Summary",
            "",
            f"- **pii_features_blocked**：{guard['pii_features_blocked']}",
            f"- **outcome_features_blocked**：{guard['outcome_features_blocked']}",
            f"- **score_date_guard**：{guard['score_date_guard']}",
            f"- **future_score_blocked_count**：{guard['future_score_blocked_count']}",
            f"- **feature_count**：{guard['feature_count']}",
            "",
            "## Demo Boundary",
            "",
        ]
    )
    for boundary in readiness["demo_boundary"]:
        lines.append(f"- {boundary}")
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            f"- {readiness['next_action']}",
            "",
            f"_Generated at {readiness['generated_at']}_",
            "",
        ]
    )
    return "\n".join(lines)


def write_ml_readiness_outputs(readiness: dict[str, Any], json_path: str | Path, md_path: str | Path) -> dict[str, str]:
    json_output = Path(json_path)
    md_output = Path(md_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    md_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_output.write_text(render_ml_readiness_report(readiness), encoding="utf-8")
    return {"readiness_json": str(json_output), "readiness_report": str(md_output)}


def _d7_candidate(dataset: pd.DataFrame) -> dict[str, Any]:
    metadata = dataset.attrs["metadata"]
    return {
        "target_id": "d7_any_payment_response",
        "decision": "selected_for_baseline",
        "grain": "loan_id",
        "row_count": int(len(dataset)),
        "positive_rate": float(metadata["positive_rate"]),
        "label_source": "dws_loan_status_snapshot_di.repaid_amount_d7 > 0",
        "leakage_risk": "low when repaid_amount_d7 and recovery_rate_d7 stay target/evaluation-only",
        "notes": "Best first baseline because the label is complete, binary, and already guarded against direct outcome leakage.",
    }


def _state_recovery_candidate(dataset: pd.DataFrame) -> dict[str, Any]:
    metadata = dataset.attrs["metadata"]
    return {
        "target_id": "d7_state_recovery_proxy",
        "decision": "feasibility_only",
        "grain": "loan_id",
        "row_count": int(len(dataset)),
        "positive_rate": float(metadata.get("state_recovery_positive_rate", metadata.get("positive_rate", 0.0))),
        "label_source": "loan daily snapshots at observation and D7",
        "leakage_risk": "medium until snapshot timing and strict cure definition are strengthened",
        "notes": "Useful for readiness diagnostics, but current synthetic strict cure positives are not strong enough for the first trainable baseline.",
    }


def _ptp_candidate(ptp_rows: pd.DataFrame) -> dict[str, Any]:
    positive_rate = float(ptp_rows["ptp_fulfilled_flag"].mean()) if len(ptp_rows) else 0.0
    return {
        "target_id": "ptp_fulfillment",
        "decision": "defer",
        "grain": "collection_action",
        "row_count": int(len(ptp_rows)),
        "positive_rate": positive_rate,
        "label_source": "ods_collection_action rows where ptp_flag is true, target ptp_fulfilled_flag",
        "leakage_risk": "medium because this is a second-stage model after promise-to-pay exists",
        "notes": "Potentially useful later, but less suitable as the first product-chain ML baseline than D7 response.",
    }
