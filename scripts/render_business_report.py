"""Render M4-C business report from M3 structured summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.report import BusinessReportInputError, write_business_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render M4-C business report from M3 summary JSON.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "outputs" / "m3" / "m3_summary.json",
        help="Path to M3 summary JSON (default: outputs/m3/m3_summary.json).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "reports" / "m4_business_report.md",
        help="Path for rendered Markdown report (default: outputs/reports/m4_business_report.md).",
    )
    parser.add_argument(
        "--html-output",
        type=Path,
        default=ROOT / "outputs" / "reports" / "m4_business_report.html",
        help="Path for rendered HTML report (default: outputs/reports/m4_business_report.html).",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Only render Markdown and skip the lightweight HTML output.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    html_output = None if args.no_html else args.html_output
    try:
        context = write_business_report(args.input, args.output, html_output)
    except BusinessReportInputError as exc:
        print(f"render_business_report failed: {exc}", file=sys.stderr)
        return 2

    overview = context["overview"]
    print(f"business report markdown: {args.output}")
    if html_output is not None:
        print(f"business report html: {html_output}")
    print(f"input: {args.input}")
    print(f"anomalies: {overview['anomaly_count']}")
    print(f"top drivers: {len(context['top_drivers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
