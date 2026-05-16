"""Metric dictionary loading and metric-code dispatch."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
METRIC_DICTIONARY_PATH = ROOT / "metadata" / "metric_dictionary.yaml"


def load_metric_dictionary(path: Path = METRIC_DICTIONARY_PATH) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("metric_dictionary.yaml must be a list of metric definitions")
    return data


def metric_by_code(path: Path = METRIC_DICTIONARY_PATH) -> dict[str, dict[str, Any]]:
    return {item["metric_code"]: item for item in load_metric_dictionary(path)}


def calculator_registry() -> dict[str, Callable[..., pd.DataFrame]]:
    from riskops.metrics.calculators.collection import COLLECTION_METRICS
    from riskops.metrics.calculators.compliance import COMPLIANCE_METRICS
    from riskops.metrics.calculators.postloan import POSTLOAN_METRICS
    from riskops.metrics.calculators.roi import ROI_METRICS

    registry: dict[str, Callable[..., pd.DataFrame]] = {}
    for group in [POSTLOAN_METRICS, COLLECTION_METRICS, COMPLIANCE_METRICS, ROI_METRICS]:
        registry.update(group)
    return registry


def calculate_metric(metric_code: str, *args: Any, **kwargs: Any) -> pd.DataFrame:
    definitions = metric_by_code()
    if metric_code not in definitions:
        raise KeyError(f"unknown metric_code: {metric_code}")
    registry = calculator_registry()
    if metric_code not in registry:
        raise KeyError(f"missing calculator for metric_code: {metric_code}")
    return registry[metric_code](*args, **kwargs)
