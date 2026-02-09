import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agentops.agents.prompts.templates import REPORT_WRITER_PROMPT
from agentops.agents.state import AgentState


async def report_writer_node(state: AgentState) -> dict:
    """Report writer agent that produces the final report."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_tokens=4000)

    fact_check_text = json.dumps(state.get("fact_check_results", []), indent=2)

    prompt = REPORT_WRITER_PROMPT.format(
        topic=state["topic"],
        summary=state.get("summary", "No summary available"),
        fact_check_results=fact_check_text[:4000],
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "report": response.content,
        "current_agent": "supervisor",
    }
