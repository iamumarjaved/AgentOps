from langgraph.graph import END, StateGraph

from agentops.agents.fact_checker import fact_checker_node
from agentops.agents.report_writer import report_writer_node
from agentops.agents.researcher import researcher_node
from agentops.agents.state import AgentState
from agentops.agents.summarizer import summarizer_node
from agentops.agents.supervisor import route_supervisor, supervisor_node


def build_graph() -> StateGraph:
    """Build the multi-agent research pipeline graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_node("fact_checker", fact_checker_node)
    graph.add_node("report_writer", report_writer_node)

    # Set entry point
    graph.set_entry_point("supervisor")

    # Add conditional edges from supervisor
    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "summarizer": "summarizer",
            "fact_checker": "fact_checker",
            "report_writer": "report_writer",
            "end": END,
        },
    )

    # All agents route back to supervisor
    for agent in ("researcher", "summarizer", "fact_checker", "report_writer"):
        graph.add_edge(agent, "supervisor")

    return graph


def compile_graph():
    """Compile the graph for execution."""
    return build_graph().compile()


async def compile_and_run(topic: str, config: dict | None = None, callbacks: list | None = None):
    """Compile and run the agent pipeline for a given topic."""
    graph = compile_graph()

    initial_state: AgentState = {
        "messages": [],
        "topic": topic,
        "research_data": [],
        "summary": "",
        "fact_check_results": [],
        "report": "",
        "current_agent": "",
        "step_count": 0,
        "metadata": config or {},
    }

    run_config = {}
    if callbacks:
        run_config["callbacks"] = callbacks

    result = await graph.ainvoke(initial_state, config=run_config)
    return result
