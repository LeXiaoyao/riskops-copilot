"""Run M3-A anomaly detection and write structured outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.anomaly.detector import AnomalyDetector
from riskops.engines.anomaly.summary import render_markdown, severity_counts, top_anomalies


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect M3-A metric anomalies from ADS/DWS outputs.")
    parser.add_argument("--data-root", type=Path, default=ROOT / "synthetic_data")
    parser.add_argument("--recent-window-days", type=int, default=30)
    parser.add_argument("--baseline-window-days", type=int, default=30)
    parser.add_argument("--output-json", type=Path, default=ROOT / "outputs" / "anomalies" / "anomaly_results.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "outputs" / "anomalies" / "anomaly_results.md")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    detector = AnomalyDetector(
        data_root=args.data_root,
        recent_window_days=args.recent_window_days,
        baseline_window_days=args.baseline_window_days,
    )
    run = detector.detect()
    payload = {
        "anomaly_count": len(run.results),
        "severity_counts": severity_counts(run.results),
        "warnings": run.warnings,
        "anomalies": [item.to_dict() for item in run.results],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(run.results, run.warnings), encoding="utf-8")

    counts = severity_counts(run.results)
    print(f"detected anomalies: {len(run.results)}")
    print(f"severity high={counts['high']} medium={counts['medium']} low={counts['low']}")
    print("top anomalies:")
    for item in top_anomalies(run.results):
        print(f"- {item.severity} {item.metric_code} {item.dimension_name}={item.dimension_value} change={item.relative_change:.2%}")
    if run.warnings:
        print("warnings:")
        for warning in run.warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
