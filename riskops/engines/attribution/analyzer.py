"""M3-B attribution analyzer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from riskops.engines.attribution.contribution import limit_dimension_candidates, score_contributions
from riskops.engines.attribution.decomposition import build_recovery_fact, infer_window, safe_rate, segment_delta
from riskops.engines.attribution.evidence import build_evidence, interpretation_for, process_metric_snapshot
from riskops.metrics.dictionary import metric_by_code

ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = ROOT / "synthetic_data"

ATTRIBUTION_DIMENSIONS = [
    "vendor_id",
    "vendor_name",
    "line_id",
    "line_name",
    "collector_id",
    "product_code",
    "channel_code",
    "province",
    "region",
    "dpd_bucket",
    "balance_segment",
    "risk_level",
    "score_band",
    "ai_call_coverage",
    "manual_call_coverage",
    "reduction_usage_rate",
    "ptp_keep_rate",
    "complaint_rate",
]


@dataclass(frozen=True)
class AttributionRun:
    results: list[dict[str, Any]]
    warnings: list[str]
    target_anomaly: dict[str, Any] | None


class AttributionAnalyzer:
    def __init__(
        self,
        data_root: Path = DATA_ROOT,
        anomaly_json: Path = ROOT / "outputs" / "anomalies" / "anomaly_results.json",
        recent_window_days: int = 30,
        baseline_window_days: int = 30,
    ) -> None:
        self.data_root = data_root
        self.anomaly_json = anomaly_json
        self.recent_window_days = recent_window_days
        self.baseline_window_days = baseline_window_days
        self.metric_definitions = metric_by_code()

    def analyze(self, target_metric: str = "recovery_rate_d7", limit: int = 10) -> AttributionRun:
        warnings: list[str] = []
        target_anomaly = self._find_target_anomaly(target_metric, warnings)
        fact = build_recovery_fact(self.data_root, warnings)
        if fact.empty:
            return AttributionRun(results=[], warnings=warnings, target_anomaly=target_anomaly)

        window = infer_window(fact, self.recent_window_days, self.baseline_window_days)
        baseline_total, recent_total = self._overall_values(fact, window)
        total_delta = recent_total - baseline_total
        segments = []
        for dimension in ATTRIBUTION_DIMENSIONS:
            if dimension not in fact.columns:
                warnings.append(f"缺少 {dimension}，该维度已跳过。")
                continue
            segment = segment_delta(fact, dimension, window)
            if segment.empty:
                warnings.append(f"{dimension} 没有可用于窗口对比的数据。")
                continue
            segments.append(segment)

        scored = score_contributions(segments, total_delta)
        scored = limit_dimension_candidates(scored, per_dimension=2).head(limit).reset_index(drop=True)
        target_name = self._metric_name(target_metric, "D7 回收率")
        anomaly_id = target_anomaly["anomaly_id"] if target_anomaly else f"M3B-{target_metric}-inferred"
        results = []
        for idx, row in scored.iterrows():
            dimension = str(row["dimension_name"])
            value = str(row["dimension_value"])
            process_metrics = process_metric_snapshot(fact, dimension, value, window)
            interpretation, action, confidence = interpretation_for(dimension, value, process_metrics)
            notes = list(dict.fromkeys(warnings))
            if target_metric == "recovery_rate_d7":
                notes.append("按 M1 dpd_bucket 过滤后解释 recovery_rate_d7，未重新定义指标口径。")
            results.append(
                {
                    "attribution_id": f"M3B-{target_metric}-{idx + 1:02d}",
                    "target_anomaly_id": anomaly_id,
                    "target_metric_code": target_metric,
                    "target_metric_name_cn": target_name,
                    "dimension_name": dimension,
                    "dimension_value": value,
                    "baseline_value": round(float(row["value_baseline"]), 6),
                    "recent_value": round(float(row["value_recent"]), 6),
                    "contribution_score": round(float(row["contribution_score"]), 6),
                    "contribution_rank": int(idx + 1),
                    "evidence": build_evidence(row, process_metrics),
                    "business_interpretation": interpretation,
                    "recommended_action": action,
                    "confidence": confidence,
                    "notes": notes,
                }
            )
        return AttributionRun(results=results, warnings=list(dict.fromkeys(warnings)), target_anomaly=target_anomaly)

    def _overall_values(self, fact: pd.DataFrame, window: Any) -> tuple[float, float]:
        baseline = fact[(fact["stat_date"] >= window.baseline_start) & (fact["stat_date"] <= window.baseline_end)]
        recent = fact[(fact["stat_date"] >= window.recent_start) & (fact["stat_date"] <= window.recent_end)]
        baseline_value = safe_rate(float(baseline["repaid_amount_d7"].sum()), float(baseline["due_amount"].sum()))
        recent_value = safe_rate(float(recent["repaid_amount_d7"].sum()), float(recent["due_amount"].sum()))
        return baseline_value, recent_value

    def _find_target_anomaly(self, target_metric: str, warnings: list[str]) -> dict[str, Any] | None:
        if not self.anomaly_json.exists():
            warnings.append(f"异常结果文件不存在：{self.anomaly_json}")
            return None
        payload = json.loads(self.anomaly_json.read_text(encoding="utf-8"))
        anomalies = payload.get("anomalies", [])
        candidates = [target_metric]
        if target_metric == "recovery_rate_d7":
            candidates.append("m1_recovery_rate")
        for item in anomalies:
            if item.get("metric_code") in candidates:
                return item
        warnings.append(f"未在异常结果中找到 {target_metric}，归因将基于当前数据窗口推断。")
        return None

    def _metric_name(self, metric_code: str, fallback: str) -> str:
        definition = self.metric_definitions.get(metric_code)
        return str(definition["metric_name_cn"]) if definition else fallback
