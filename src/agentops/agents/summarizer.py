import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agentops.agents.prompts.templates import SUMMARIZER_PROMPT
from agentops.agents.state import AgentState


async def summarizer_node(state: AgentState) -> dict:
    """Summarizer agent that condenses research data."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    research_text = "\n\n---\n\n".join(
        f"Source: {item.get('source', 'unknown')}\n{item.get('content', '')}"
        for item in state.get("research_data", [])
    )

    prompt = SUMMARIZER_PROMPT.format(
        topic=state["topic"],
        research_data=research_text[:8000],  # Truncate to fit context
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "summary": response.content,
        "current_agent": "supervisor",
    }
