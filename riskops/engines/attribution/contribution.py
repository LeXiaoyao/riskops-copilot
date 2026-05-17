"""Contribution scoring for attribution candidates."""

from __future__ import annotations

import pandas as pd


def score_contributions(segments: list[pd.DataFrame], total_delta: float, min_recent_weight: float = 0.005) -> pd.DataFrame:
    if not segments:
        return pd.DataFrame()
    combined = pd.concat([frame for frame in segments if not frame.empty], ignore_index=True)
    if combined.empty:
        return combined

    dimension_denominator = combined.groupby("dimension_name")["denominator_recent"].transform("sum")
    if float(dimension_denominator.max()) <= 0:
        combined["contribution_score"] = 0.0
        return combined

    combined["recent_weight"] = combined["denominator_recent"] / dimension_denominator.replace(0, pd.NA)
    combined["raw_contribution"] = combined["delta"] * combined["recent_weight"]
    if total_delta < 0:
        combined["adverse_contribution"] = (-combined["raw_contribution"]).clip(lower=0)
    else:
        combined["adverse_contribution"] = combined["raw_contribution"].clip(lower=0)
    denominator = abs(total_delta) if abs(total_delta) > 0 else 1.0
    combined["contribution_score"] = combined["adverse_contribution"] / denominator
    combined = combined[combined["recent_weight"] >= min_recent_weight].copy()
    combined = combined[combined["contribution_score"] > 0].copy()
    total_adverse = float(combined["adverse_contribution"].sum())
    if total_adverse > 0:
        combined["contribution_score"] = combined["adverse_contribution"] / total_adverse
    return combined.sort_values(["contribution_score", "denominator_recent"], ascending=[False, False])


def limit_dimension_candidates(scored: pd.DataFrame, per_dimension: int = 2) -> pd.DataFrame:
    if scored.empty:
        return scored
    return scored.groupby("dimension_name", group_keys=False).head(per_dimension).reset_index(drop=True)
