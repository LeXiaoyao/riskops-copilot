"""Render M3-C structured anomaly attribution report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.report import M3ReportInputError, write_m3_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render M3-C report from anomaly and attribution outputs.")
    parser.add_argument("--anomaly-json", type=Path, default=ROOT / "outputs" / "anomalies" / "anomaly_results.json")
    parser.add_argument("--attribution-json", type=Path, default=ROOT / "outputs" / "attribution" / "attribution_results.json")
    parser.add_argument("--output-json", type=Path, default=ROOT / "outputs" / "m3" / "m3_summary.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "outputs" / "m3" / "m3_summary.md")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = write_m3_report(args.anomaly_json, args.attribution_json, args.output_json, args.output_md)
    except M3ReportInputError as exc:
        print(f"render_m3_report failed: {exc}", file=sys.stderr)
        return 2

    overview = summary["anomaly_overview"]
    attribution = summary["m1_d7_attribution_summary"]
    print(f"m3 report json: {args.output_json}")
    print(f"m3 report markdown: {args.output_md}")
    print(f"anomalies: {overview['anomaly_count']}")
    print(f"top drivers: {len(attribution['top_drivers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
