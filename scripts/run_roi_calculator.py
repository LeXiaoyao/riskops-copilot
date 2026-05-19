"""Run M6-C1 ROI calculator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.model_lab.roi_calculator import (
    calculate_roi_results,
    load_strategy_eval_results,
    write_roi_outputs,
)

DEFAULT_STRATEGY_EVAL = ROOT / "outputs" / "model_lab" / "strategy_eval_results.json"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "model_lab" / "roi_results.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "model_lab" / "roi_summary.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M6-C1 ROI calculator.")
    parser.add_argument("--strategy-eval", type=Path, default=DEFAULT_STRATEGY_EVAL)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        strategy_eval_results = load_strategy_eval_results(args.strategy_eval)
        report = calculate_roi_results(strategy_eval_results)
        write_roi_outputs(report, args.output_json, args.output_md)
    except (FileNotFoundError, ValueError) as exc:
        print("FAIL ROI calculator")
        print(f"ERROR {exc}")
        return 1

    highest = report.get("highest_roi_scenario") or {}
    highest_label = highest.get("scenario_id", "none")
    print(f"scenario count: {report['scenario_count']}")
    print(f"positive ROI scenarios: {report['positive_roi_count']}")
    print(f"highest ROI scenario: {highest_label}")
    print(f"output json: {args.output_json}")
    print(f"output markdown: {args.output_md}")
    print("PASS ROI calculator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
