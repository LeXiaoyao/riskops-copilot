"""Static HTML dashboard engine (M4-A/B MVP)."""

from riskops.engines.dashboard.dashboard_builder import (
    DashboardInputError,
    build_dashboard_context,
    render_dashboard_html,
    write_dashboard,
)

__all__ = [
    "DashboardInputError",
    "build_dashboard_context",
    "render_dashboard_html",
    "write_dashboard",
]
