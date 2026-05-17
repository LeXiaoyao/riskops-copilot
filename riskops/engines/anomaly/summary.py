"""Formatting helpers for anomaly detection outputs."""

from __future__ import annotations

from collections import Counter

from riskops.engines.anomaly.models import AnomalyResult


def severity_counts(results: list[AnomalyResult]) -> dict[str, int]:
    counts = Counter(item.severity for item in results)
    return {severity: counts.get(severity, 0) for severity in ["high", "medium", "low"]}


def top_anomalies(results: list[AnomalyResult], limit: int = 5) -> list[AnomalyResult]:
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(results, key=lambda item: (order[item.severity], -abs(item.relative_change), item.metric_code))[:limit]


def render_markdown(results: list[AnomalyResult], warnings: list[str]) -> str:
    lines = ["# M3-A 异常检测结果", ""]
    counts = severity_counts(results)
    lines.extend(
        [
            f"- 检测异常数：{len(results)}",
            f"- high：{counts['high']}",
            f"- medium：{counts['medium']}",
            f"- low：{counts['low']}",
            "",
            "## Top anomalies",
            "",
        ]
    )
    for idx, item in enumerate(top_anomalies(results), start=1):
        lines.extend(
            [
                f"### {idx}. {item.metric_name_cn}",
                f"- metric_code：{item.metric_code}",
                f"- severity：{item.severity}",
                f"- dimension：{item.dimension_name}={item.dimension_value}",
                f"- baseline_value：{item.baseline_value:.6f}",
                f"- recent_value：{item.recent_value:.6f}",
                f"- change：{item.absolute_change:.6f} / {item.relative_change:.2%}",
                f"- evidence_table：{item.evidence_table}",
                f"- explanation：{item.explanation}",
                f"- recommended_next_step：{item.recommended_next_step}",
                "",
            ]
        )
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    return "\n".join(lines)
