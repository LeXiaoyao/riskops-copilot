"""Render M4-A/B static HTML dashboard from M3 structured summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.dashboard import DashboardInputError, write_dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render static HTML dashboard (M4-A/B MVP) from M3 summary JSON.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "outputs" / "m3" / "m3_summary.json",
        help="Path to M3 summary JSON (default: outputs/m3/m3_summary.json).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "dashboard" / "dashboard.html",
        help="Path for the rendered dashboard HTML (default: outputs/dashboard/dashboard.html).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        context = write_dashboard(args.input, args.output)
    except DashboardInputError as exc:
        print(f"render_dashboard failed: {exc}", file=sys.stderr)
        return 2

    overview = context["overview"]
    print(f"dashboard html: {args.output}")
    print(f"input: {args.input}")
    print(f"anomalies: {overview['anomaly_count']}")
    print(f"top drivers: {len(context['top_drivers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
