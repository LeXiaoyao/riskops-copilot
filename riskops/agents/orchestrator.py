"""Agent orchestrator for RiskOps Copilot."""

from __future__ import annotations

from collections.abc import Iterator

from riskops.agents.collection_strategy import CollectionStrategyAgent
from riskops.agents.compliance_qa import ComplianceQAAgent
from riskops.agents.report_writer import ReportWriterAgent
from riskops.agents.risk_analyst import RiskAnalystAgent


class RiskOpsOrchestrator:
    def __init__(self, api_key: str | None, model: str = "deepseek-chat") -> None:
        self.api_key = api_key
        self.model = model
        self._agents = None

    def _get_agents(self) -> dict[str, object]:
        if self._agents is None:
            self._agents = {
                "risk": RiskAnalystAgent(self.api_key, self.model),
                "collection": CollectionStrategyAgent(self.api_key, self.model),
                "compliance": ComplianceQAAgent(self.api_key, self.model),
                "report": ReportWriterAgent(self.api_key, self.model),
            }
        return self._agents

    def route(self, message: str) -> str:
        """Route a user message to the most relevant specialist agent."""

        msg = message.lower()
        if any(k in msg for k in ["质检", "合规", "红线", "话术检查", "录音", "违规"]):
            return "compliance"
        if any(k in msg for k in ["话术", "短信", "草稿", "发送", "催收脚本", "催收案件"]):
            return "collection"
        if any(k in msg for k in ["报告", "周报", "ppt", "excel", "word", "导出"]):
            return "report"
        return "risk"

    def run(self, message: str) -> Iterator[str]:
        """Route a message and stream the selected agent result."""

        agent_key = self.route(message)
        agent = self._get_agents()[agent_key]
        yield f"**[→ {agent.display_name}]**\n\n"
        yield from agent.run(message)
