"""Script entry point for the M5 RiskOps CLI MVP."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.interfaces.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

