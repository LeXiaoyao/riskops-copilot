"""Data models for anomaly detection results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

AnomalyType = Literal["window_compare", "trend_drop", "spike", "ratio_to_average", "threshold"]
Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class AnomalyConfig:
    recent_window_days: int = 30
    baseline_window_days: int = 30
    min_relative_change: float = 0.10
    min_absolute_change_pct: float = 0.02
    complaint_multiplier_threshold: float = 2.0
    severity_thresholds: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            "low": {"min_relative_change": 0.10, "min_absolute_change_pct": 0.02},
            "medium": {"min_relative_change": 0.15, "min_absolute_change_pct": 0.04},
            "high": {"min_relative_change": 0.25, "min_absolute_change_pct": 0.06},
        }
    )


@dataclass(frozen=True)
class AnomalyResult:
    anomaly_id: str
    metric_code: str
    metric_name_cn: str
    anomaly_type: AnomalyType
    severity: Severity
    dimension_name: str
    dimension_value: str
    baseline_value: float
    recent_value: float
    absolute_change: float
    relative_change: float
    recent_window: str
    baseline_window: str
    evidence_table: str
    explanation: str
    recommended_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
