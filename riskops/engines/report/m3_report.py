"""Structured M3 anomaly attribution report renderer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

REPORT_VERSION = "m3-c-v1"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


class M3ReportInputError(RuntimeError):
    """Raised when required M3 report inputs are missing or malformed."""


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise M3ReportInputError(f"输入文件不存在：{path}。请先生成 {label}。")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise M3ReportInputError(f"输入文件不是合法 JSON：{path}。错误：{exc}") from exc
    if not isinstance(payload, dict):
        raise M3ReportInputError(f"输入文件结构不符合预期：{path} 顶层必须是 JSON object。")
    return payload


def build_m3_summary(
    anomaly_payload: dict[str, Any],
    attribution_payload: dict[str, Any],
    source_files: dict[str, str] | None = None,
    top_driver_limit: int = 5,
) -> dict[str, Any]:
    anomalies = _as_list(anomaly_payload.get("anomalies"))
    attributions = sorted(
        _as_list(attribution_payload.get("attributions")),
        key=lambda item: int(item.get("contribution_rank", 9999)),
    )
    top_drivers = [_driver_summary(item) for item in attributions[:top_driver_limit]]
    target_anomaly_id = attribution_payload.get("target_anomaly_id")
    target_anomaly = _find_anomaly(anomalies, target_anomaly_id)
    high_priority_anomalies = [item for item in anomalies if item.get("severity") == "high"]

    return {
        "report_version": REPORT_VERSION,
        "source_files": source_files or {},
        "anomaly_overview": {
            "anomaly_count": int(anomaly_payload.get("anomaly_count", len(anomalies))),
            "severity_counts": anomaly_payload.get("severity_counts", {}),
            "warnings": _as_list(anomaly_payload.get("warnings")),
            "baseline_window": _first_non_empty(anomalies, "baseline_window"),
            "recent_window": _first_non_empty(anomalies, "recent_window"),
        },
        "high_priority_anomalies": high_priority_anomalies,
        "m1_d7_attribution_summary": {
            "target_metric_code": attribution_payload.get("target_metric_code"),
            "target_metric_name_cn": _first_non_empty(attributions, "target_metric_name_cn"),
            "target_anomaly_id": target_anomaly_id,
            "target_anomaly": target_anomaly,
            "attribution_count": int(attribution_payload.get("attribution_count", len(attributions))),
            "warnings": _as_list(attribution_payload.get("warnings")),
            "primary_driver": top_drivers[0] if top_drivers else None,
            "top_drivers": top_drivers,
        },
        "process_evidence": _process_evidence(top_drivers),
        "business_recommendations": _business_recommendations(top_drivers, high_priority_anomalies),
        "data_limitations": _data_limitations(anomaly_payload, attribution_payload, top_drivers),
        "next_steps": _next_steps(top_drivers, high_priority_anomalies),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )
    env.filters["pct"] = _format_pct
    env.filters["number"] = _format_number
    return env.get_template("m3_summary.md.j2").render(summary=summary).rstrip() + "\n"


def write_m3_report(
    anomaly_json: Path,
    attribution_json: Path,
    output_json: Path,
    output_md: Path,
) -> dict[str, Any]:
    anomaly_payload = read_json(anomaly_json, "M3-A anomaly results")
    attribution_payload = read_json(attribution_json, "M3-B attribution results")
    summary = build_m3_summary(
        anomaly_payload,
        attribution_payload,
        source_files={
            "anomaly_results": _path_for_report(anomaly_json),
            "attribution_results": _path_for_report(attribution_json),
        },
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(summary), encoding="utf-8")
    return summary


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _path_for_report(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _find_anomaly(anomalies: list[dict[str, Any]], anomaly_id: Any) -> dict[str, Any] | None:
    for item in anomalies:
        if item.get("anomaly_id") == anomaly_id:
            return item
    return None


def _first_non_empty(items: list[dict[str, Any]], key: str) -> Any:
    for item in items:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def _driver_summary(item: dict[str, Any]) -> dict[str, Any]:
    evidence = _as_list(item.get("evidence"))
    return {
        "attribution_id": item.get("attribution_id"),
        "rank": item.get("contribution_rank"),
        "dimension_name": item.get("dimension_name"),
        "dimension_value": item.get("dimension_value"),
        "baseline_value": item.get("baseline_value"),
        "recent_value": item.get("recent_value"),
        "contribution_score": item.get("contribution_score"),
        "business_interpretation": item.get("business_interpretation"),
        "recommended_action": item.get("recommended_action"),
        "confidence": item.get("confidence"),
        "segment_evidence": [entry for entry in evidence if entry.get("method") == "segment_delta"],
        "driver_linkage": [entry for entry in evidence if entry.get("method") == "driver_linkage"],
        "notes": _as_list(item.get("notes")),
    }


def _process_evidence(top_drivers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence_rows: list[dict[str, Any]] = []
    for driver in top_drivers:
        for item in driver["driver_linkage"]:
            evidence_rows.append(
                {
                    "attribution_id": driver["attribution_id"],
                    "driver": f"{driver['dimension_name']}={driver['dimension_value']}",
                    "metric_code": item.get("metric_code"),
                    "metric_name_cn": item.get("metric_name_cn"),
                    "baseline_value": item.get("baseline_value"),
                    "recent_value": item.get("recent_value"),
                    "delta": item.get("delta"),
                    "method": item.get("method"),
                }
            )
    return evidence_rows


def _business_recommendations(top_drivers: list[dict[str, Any]], high_priority_anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for driver in top_drivers:
        action = driver.get("recommended_action")
        if isinstance(action, str) and action and action not in seen:
            seen.add(action)
            items.append(
                {
                    "source": "attribution",
                    "source_id": driver.get("attribution_id"),
                    "driver": f"{driver.get('dimension_name')}={driver.get('dimension_value')}",
                    "recommendation": action,
                }
            )
    for anomaly in high_priority_anomalies:
        action = anomaly.get("recommended_next_step")
        if isinstance(action, str) and action and action not in seen:
            seen.add(action)
            items.append(
                {
                    "source": "anomaly",
                    "source_id": anomaly.get("anomaly_id"),
                    "driver": f"{anomaly.get('metric_code')}:{anomaly.get('dimension_name')}={anomaly.get('dimension_value')}",
                    "recommendation": action,
                }
            )
    return items


def _data_limitations(
    anomaly_payload: dict[str, Any],
    attribution_payload: dict[str, Any],
    top_drivers: list[dict[str, Any]],
) -> list[dict[str, str]]:
    limitations: list[dict[str, str]] = []
    for warning in _as_list(anomaly_payload.get("warnings")):
        limitations.append({"source": "anomaly_warning", "description": str(warning)})
    for warning in _as_list(attribution_payload.get("warnings")):
        limitations.append({"source": "attribution_warning", "description": str(warning)})

    notes: list[str] = []
    for driver in top_drivers:
        for note in driver["notes"]:
            if isinstance(note, str) and note not in notes:
                notes.append(note)
    for note in notes:
        limitations.append({"source": "attribution_note", "description": note})

    if not limitations:
        limitations.append({"source": "input_status", "description": "上游 anomaly_results 与 attribution_results 未返回 warnings。"})
    limitations.append(
        {
            "source": "method_boundary",
            "description": "贡献度为各维度切片的边际贡献，跨维度可能重叠，不可直接相加为整体下降的解释比例。",
        }
    )
    return limitations


def _next_steps(top_drivers: list[dict[str, Any]], high_priority_anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    next_steps: list[dict[str, Any]] = []
    for item in _business_recommendations(top_drivers, high_priority_anomalies)[:8]:
        next_steps.append(
            {
                "source": item["source"],
                "source_id": item["source_id"],
                "next_step": item["recommendation"],
            }
        )
    return next_steps


def _format_pct(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.2%}"
    return "N/A"


def _format_number(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.6f}"
    return "N/A"
