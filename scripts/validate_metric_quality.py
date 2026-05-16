"""CLI placeholder for metric quality validation."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate RiskOps metric quality rules. M0 placeholder only."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate CLI wiring without checking metric quality.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    parser.parse_args()
    # TODO: Implement in M2 after metric dictionary and calculators land.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
