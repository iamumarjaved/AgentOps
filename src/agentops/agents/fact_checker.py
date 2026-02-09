import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agentops.agents.prompts.templates import FACT_CHECKER_PROMPT
from agentops.agents.state import AgentState


async def fact_checker_node(state: AgentState) -> dict:
    """Fact checker agent that verifies claims in the summary."""
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    prompt = FACT_CHECKER_PROMPT.format(
        topic=state["topic"],
        summary=state.get("summary", "No summary available"),
    ) + "\n\nRespond in JSON format with a list of fact checks: {\"checks\": [{\"claim\": \"...\", \"confidence\": \"high/medium/low\", \"notes\": \"...\"}]}"

    response = await llm.ainvoke([HumanMessage(content=prompt)])

    try:
        fact_checks = json.loads(response.content)
        checks = fact_checks.get("checks", [])
    except (json.JSONDecodeError, AttributeError):
        checks = [{"claim": "Unable to parse fact check results", "confidence": "low", "notes": response.content}]

    return {
        "fact_check_results": checks,
        "current_agent": "supervisor",
    }
