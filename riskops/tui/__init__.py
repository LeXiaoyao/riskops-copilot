"""RiskOps Copilot TUI entry point."""

from __future__ import annotations

from riskops.tui.app import RiskOpsTUIApp


def run() -> None:
    app = RiskOpsTUIApp()
    app.run()
