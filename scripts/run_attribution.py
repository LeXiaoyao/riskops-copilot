"""Run M3-B attribution analysis and write structured outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.attribution.analyzer import AttributionAnalyzer
from riskops.engines.attribution.summary import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M3-B attribution analysis for anomaly results.")
    parser.add_argument("--data-root", type=Path, default=ROOT / "synthetic_data")
    parser.add_argument("--anomaly-json", type=Path, default=ROOT / "outputs" / "anomalies" / "anomaly_results.json")
    parser.add_argument("--target-metric", default="recovery_rate_d7")
    parser.add_argument("--output-json", type=Path, default=ROOT / "outputs" / "attribution" / "attribution_results.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "outputs" / "attribution" / "attribution_summary.md")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    analyzer = AttributionAnalyzer(data_root=args.data_root, anomaly_json=args.anomaly_json)
    run = analyzer.analyze(target_metric=args.target_metric)
    payload = {
        "target_metric_code": args.target_metric,
        "target_anomaly_id": run.target_anomaly["anomaly_id"] if run.target_anomaly else None,
        "attribution_count": len(run.results),
        "warnings": run.warnings,
        "attributions": run.results,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(run.results, run.warnings), encoding="utf-8")

    print(f"attributions: {len(run.results)}")
    for item in run.results[:5]:
        print(
            f"- rank={item['contribution_rank']} {item['dimension_name']}={item['dimension_value']} "
            f"score={item['contribution_score']:.2%}"
        )
    if run.warnings:
        print("warnings:")
        for warning in run.warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
