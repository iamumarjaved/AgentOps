from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agentops.agents.prompts.templates import SUPERVISOR_PROMPT
from agentops.agents.state import AgentState


async def supervisor_node(state: AgentState) -> dict:
    """Supervisor decides which agent acts next."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=50)

    prompt = SUPERVISOR_PROMPT.format(
        topic=state["topic"],
        has_research=bool(state.get("research_data")),
        has_summary=bool(state.get("summary")),
        has_fact_check=bool(state.get("fact_check_results")),
        has_report=bool(state.get("report")),
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    next_agent = response.content.strip().lower()

    return {
        "current_agent": next_agent,
        "step_count": state.get("step_count", 0) + 1,
    }


def route_supervisor(state: AgentState) -> str:
    """Route to the next agent based on supervisor decision."""
    agent = state.get("current_agent", "")

    if agent == "finish" or state.get("step_count", 0) > 10:
        return "end"
    if agent in ("researcher", "summarizer", "fact_checker", "report_writer"):
        return agent
    return "end"
