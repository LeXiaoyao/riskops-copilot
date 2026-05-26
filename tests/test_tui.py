from __future__ import annotations

from riskops.tui.app import SLASH_COMMANDS, RiskOpsTUIApp
from riskops.tui.chat_client import TOOL_SCHEMAS
from riskops.tui.context_loader import load_context
from riskops.tui.tools import get_data_overview, query_anomalies, query_recovery_rate


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


def test_tool_schemas_include_local_query_tools() -> None:
    names = {item["function"]["name"] for item in TOOL_SCHEMAS}

    assert "query_recovery_rate" in names
    assert "query_anomalies" in names
    assert "get_data_overview" in names


def test_recovery_rate_tool_returns_series() -> None:
    result = query_recovery_rate(date_start="2026-04-01", date_end="2026-04-07")

    assert result["tool"] == "query_recovery_rate"
    assert result["row_count"] > 0
    assert result["result"]
    assert "recovery_rate_d7" in result["result"][0]


def test_anomaly_tool_can_filter_severity() -> None:
    result = query_anomalies(severity="high")

    assert result["tool"] == "query_anomalies"
    assert all(item["severity"] == "high" for item in result["result"])


def test_data_overview_tool_lists_queryable_files() -> None:
    result = get_data_overview()

    assert result["tool"] == "get_data_overview"
    assert result["row_count"] > 0
    assert result["result"]
