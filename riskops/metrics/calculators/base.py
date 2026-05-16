"""Shared helpers for metric calculators."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = ROOT / "synthetic_data"


def read_table(root: Path, layer: str, table: str) -> pd.DataFrame:
    for suffix in ["parquet", "csv"]:
        path = root / layer / f"{table}.{suffix}"
        if path.exists():
            return pd.read_parquet(path) if suffix == "parquet" else pd.read_csv(path)
    raise FileNotFoundError(f"missing table: {layer}/{table}")


def safe_rate(num: pd.Series | np.ndarray, den: pd.Series | np.ndarray, *, clip: bool = True) -> pd.Series:
    numerator = np.asarray(num, dtype=float)
    denominator = np.asarray(den, dtype=float)
    result = np.zeros_like(numerator, dtype=float)
    np.divide(numerator, denominator, out=result, where=denominator > 0)
    series = pd.Series(result)
    if clip:
        series = series.clip(0, 1)
    return series.round(6)


def as_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.date


def full_date_frame(*frames: pd.DataFrame) -> pd.DataFrame:
    dates: set[object] = set()
    for frame in frames:
        if "stat_date" in frame:
            dates.update(frame["stat_date"].dropna().tolist())
    return pd.DataFrame({"stat_date": sorted(dates)})


def empty_daily(metric_code: str) -> pd.DataFrame:
    return pd.DataFrame(columns=["stat_date", metric_code])
