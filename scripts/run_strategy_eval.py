"""Run M6-B offline strategy evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.model_lab.strategy_evaluator import run_strategy_evaluation

DEFAULT_SCENARIOS = ROOT / "configs" / "strategy_scenarios.yaml"
DEFAULT_M3_SUMMARY = ROOT / "outputs" / "m3" / "m3_summary.json"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "model_lab" / "strategy_eval_results.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "model_lab" / "strategy_eval_summary.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M6-B offline strategy evaluator.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--m3-summary", type=Path, default=DEFAULT_M3_SUMMARY)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_strategy_evaluation(
            scenarios_path=args.scenarios,
            m3_summary_path=args.m3_summary,
            output_json=args.output_json,
            output_md=args.output_md,
        )
    except (FileNotFoundError, ValueError) as exc:
        print("FAIL strategy evaluation")
        print(f"ERROR {exc}")
        return 1

    print(f"scenario count: {report['scenario_count']}")
    print("strategy_type counts:")
    for strategy_type, count in report["strategy_type_counts"].items():
        print(f"- {strategy_type}: {count}")
    print(f"target_metric: {', '.join(report['target_metric_counts'].keys())}")
    print(f"output json: {args.output_json}")
    print(f"output markdown: {args.output_md}")
    print("PASS strategy evaluation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
