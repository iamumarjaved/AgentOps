import pytest

from agentops.agents.state import AgentState
from agentops.agents.supervisor import route_supervisor


class TestSupervisorRouting:
    def test_route_to_researcher(self):
        state: AgentState = {
            "messages": [],
            "topic": "test",
            "research_data": [],
            "summary": "",
            "fact_check_results": [],
            "report": "",
            "current_agent": "researcher",
            "step_count": 1,
            "metadata": {},
        }
        assert route_supervisor(state) == "researcher"

    def test_route_to_summarizer(self):
        state: AgentState = {
            "messages": [],
            "topic": "test",
            "research_data": [],
            "summary": "",
            "fact_check_results": [],
            "report": "",
            "current_agent": "summarizer",
            "step_count": 2,
            "metadata": {},
        }
        assert route_supervisor(state) == "summarizer"

    def test_route_to_end_on_finish(self):
        state: AgentState = {
            "messages": [],
            "topic": "test",
            "research_data": [],
            "summary": "",
            "fact_check_results": [],
            "report": "",
            "current_agent": "finish",
            "step_count": 5,
            "metadata": {},
        }
        assert route_supervisor(state) == "end"

    def test_route_to_end_on_max_steps(self):
        state: AgentState = {
            "messages": [],
            "topic": "test",
            "research_data": [],
            "summary": "",
            "fact_check_results": [],
            "report": "",
            "current_agent": "researcher",
            "step_count": 11,
            "metadata": {},
        }
        assert route_supervisor(state) == "end"

    def test_route_unknown_agent_to_end(self):
        state: AgentState = {
            "messages": [],
            "topic": "test",
            "research_data": [],
            "summary": "",
            "fact_check_results": [],
            "report": "",
            "current_agent": "unknown_agent",
            "step_count": 1,
            "metadata": {},
        }
        assert route_supervisor(state) == "end"
