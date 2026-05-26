"""RiskOps Copilot TUI entry point."""

from __future__ import annotations

def run() -> None:
    from riskops.tui.app import RiskOpsTUIApp

    app = RiskOpsTUIApp()
    app.run()
