from __future__ import annotations

from collections.abc import Iterator

from riskops.agents.orchestrator import RiskOpsOrchestrator
from riskops.agents.risk_analyst import RiskAnalystAgent


def test_route_risk_keywords() -> None:
    orch = RiskOpsOrchestrator(api_key="test")

    assert orch.route("回收率为什么下降") == "risk"


def test_route_compliance_keywords() -> None:
    orch = RiskOpsOrchestrator(api_key="test")

    assert orch.route("质检这条话术") == "compliance"


def test_route_collection_keywords() -> None:
    orch = RiskOpsOrchestrator(api_key="test")

    assert orch.route("给案件生成话术草稿") == "collection"


def test_route_report_keywords() -> None:
    orch = RiskOpsOrchestrator(api_key="test")

    assert orch.route("生成周报PPT") == "report"


def test_orchestrator_init() -> None:
    orch = RiskOpsOrchestrator(api_key="test")

    assert orch.model == "deepseek-chat"


def test_risk_analyst_init() -> None:
    agent = RiskAnalystAgent(api_key="test")

    assert agent.display_name == "风险分析专家"


def test_orchestrator_run_yields_string(monkeypatch) -> None:
    class FakeRiskAgent:
        display_name = "风险分析专家"

        def run(self, message: str) -> Iterator[str]:
            yield "mock answer"

    orch = RiskOpsOrchestrator(api_key="test")
    monkeypatch.setattr(orch, "_get_agents", lambda: {"risk": FakeRiskAgent()})

    stream = orch.run("回收率为什么下降")
    first = next(stream)

    assert isinstance(first, str)
    assert "风险分析专家" in first
