"""Validate M6-A strategy scenario config."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.engines.model_lab.scenario_schema import (
    load_strategy_scenarios,
    summarize_strategy_scenarios,
    validate_strategy_scenarios,
)

DEFAULT_CONFIG = ROOT / "configs" / "strategy_scenarios.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate M6-A strategy scenario schema.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        scenarios = load_strategy_scenarios(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print("FAIL strategy_scenarios validation")
        print(f"ERROR {exc}")
        return 1

    summary = summarize_strategy_scenarios(scenarios)
    errors = validate_strategy_scenarios(scenarios)

    print(f"scenario count: {summary['scenario_count']}")
    print("strategy_type counts:")
    for strategy_type, count in summary["strategy_type_counts"].items():
        print(f"- {strategy_type}: {count}")
    print("target_metric counts:")
    for target_metric, count in summary["target_metric_counts"].items():
        print(f"- {target_metric}: {count}")

    if errors:
        print("FAIL strategy_scenarios validation")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS strategy_scenarios validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
