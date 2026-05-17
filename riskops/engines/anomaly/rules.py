"""Statistical rules for the M3-A anomaly engine."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from riskops.engines.anomaly.models import AnomalyConfig, Severity

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = ROOT / "configs" / "anomaly_rules.yaml"


def load_anomaly_config(path: Path = DEFAULT_CONFIG_PATH) -> AnomalyConfig:
    if not path.exists():
        return AnomalyConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    allowed = set(AnomalyConfig.__dataclass_fields__)
    clean: dict[str, Any] = {key: value for key, value in data.items() if key in allowed}
    return replace(AnomalyConfig(), **clean)


def window_bounds(series: pd.DataFrame, date_col: str, recent_days: int, baseline_days: int) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    dates = pd.to_datetime(series[date_col], errors="coerce").dropna()
    if dates.empty:
        raise ValueError("date column has no valid values")
    max_date = dates.max().normalize()
    recent_start = max_date - pd.Timedelta(days=recent_days - 1)
    baseline_end = recent_start - pd.Timedelta(days=1)
    baseline_start = baseline_end - pd.Timedelta(days=baseline_days - 1)
    return baseline_start, baseline_end, recent_start, max_date


def window_means(
    series: pd.DataFrame,
    date_col: str,
    value_col: str,
    recent_days: int,
    baseline_days: int,
) -> tuple[float, float, str, str]:
    baseline_start, baseline_end, recent_start, recent_end = window_bounds(series, date_col, recent_days, baseline_days)
    frame = series.copy()
    frame[date_col] = pd.to_datetime(frame[date_col], errors="coerce")
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    baseline = frame[(frame[date_col] >= baseline_start) & (frame[date_col] <= baseline_end)][value_col].dropna()
    recent = frame[(frame[date_col] >= recent_start) & (frame[date_col] <= recent_end)][value_col].dropna()
    if baseline.empty or recent.empty:
        raise ValueError(f"{value_col} lacks baseline or recent observations")
    return (
        float(baseline.mean()),
        float(recent.mean()),
        f"{recent_start.date()}~{recent_end.date()}",
        f"{baseline_start.date()}~{baseline_end.date()}",
    )


def relative_change(baseline_value: float, recent_value: float) -> float:
    if baseline_value == 0:
        return 0.0
    return (recent_value - baseline_value) / abs(baseline_value)


def is_window_anomaly(
    baseline_value: float,
    recent_value: float,
    direction: str,
    config: AnomalyConfig,
    min_relative_change: float | None = None,
    min_absolute_change_pct: float | None = None,
) -> bool:
    absolute_change = recent_value - baseline_value
    rel_change = relative_change(baseline_value, recent_value)
    if direction == "drop":
        directional = absolute_change < 0
        magnitude = -rel_change
        absolute_magnitude = -absolute_change
    elif direction == "increase":
        directional = absolute_change > 0
        magnitude = rel_change
        absolute_magnitude = absolute_change
    else:
        directional = abs(absolute_change) > 0
        magnitude = abs(rel_change)
        absolute_magnitude = abs(absolute_change)
    return directional and (
        magnitude >= (min_relative_change if min_relative_change is not None else config.min_relative_change)
        or absolute_magnitude >= (min_absolute_change_pct if min_absolute_change_pct is not None else config.min_absolute_change_pct)
    )


def classify_severity(absolute_change: float, rel_change: float, config: AnomalyConfig) -> Severity:
    magnitude = abs(rel_change)
    absolute_magnitude = abs(absolute_change)
    high = config.severity_thresholds.get("high", {})
    medium = config.severity_thresholds.get("medium", {})
    if magnitude >= high.get("min_relative_change", 0.25) or absolute_magnitude >= high.get("min_absolute_change_pct", 0.06):
        return "high"
    if magnitude >= medium.get("min_relative_change", 0.15) or absolute_magnitude >= medium.get("min_absolute_change_pct", 0.04):
        return "medium"
    return "low"


def trend_drop(series: pd.DataFrame, value_col: str, points: int = 5) -> bool:
    values = pd.to_numeric(series.sort_values("stat_date").tail(points)[value_col], errors="coerce").dropna()
    return len(values) == points and all(values.iloc[idx] < values.iloc[idx - 1] for idx in range(1, points))


def spike(recent_value: float, baseline_value: float, config: AnomalyConfig) -> bool:
    return is_window_anomaly(baseline_value, recent_value, "increase", config)


def threshold(value: float, threshold_value: float, direction: str = "above") -> bool:
    return value > threshold_value if direction == "above" else value < threshold_value
