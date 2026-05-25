from __future__ import annotations

from riskops.tui.app import SLASH_COMMANDS, RiskOpsTUIApp
from riskops.tui.context_loader import load_context


def test_app_can_instantiate() -> None:
    app = RiskOpsTUIApp()

    assert app is not None


def test_context_loader_returns_string() -> None:
    ctx = load_context()

    assert isinstance(ctx, str)
    assert len(ctx) > 0


def test_slash_commands_recognized() -> None:
    for command in [
        "/help",
        "/clear",
        "/summary",
        "/anomaly",
        "/drivers",
        "/roi",
        "/briefing",
        "/model",
    ]:
        assert command in SLASH_COMMANDS
