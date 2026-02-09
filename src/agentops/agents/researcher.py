import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agentops.agents.prompts.templates import RESEARCHER_PROMPT
from agentops.agents.state import AgentState
from agentops.agents.tools.arxiv_tool import arxiv_search
from agentops.agents.tools.scraper import scrape_url
from agentops.agents.tools.web_search import web_search
from agentops.agents.tools.wikipedia_tool import wikipedia_search

TOOLS = [web_search, wikipedia_search, arxiv_search, scrape_url]


async def researcher_node(state: AgentState) -> dict:
    """Research agent that gathers information using tools."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1).bind_tools(TOOLS)

    prompt = RESEARCHER_PROMPT.format(topic=state["topic"])
    messages = [HumanMessage(content=prompt)]

    research_data = list(state.get("research_data", []))
    iterations = 0

    while iterations < 3:
        response = await llm.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            # LLM done calling tools — extract final research
            research_data.append({
                "source": "llm_synthesis",
                "content": response.content,
            })
            break

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tool_map = {
                "web_search": web_search,
                "wikipedia_search": wikipedia_search,
                "arxiv_search": arxiv_search,
                "scrape_url": scrape_url,
            }

            tool_fn = tool_map.get(tool_name)
            if tool_fn:
                result = await tool_fn.ainvoke(tool_args)
                research_data.append({
                    "source": tool_name,
                    "query": json.dumps(tool_args),
                    "content": str(result),
                })
                from langchain_core.messages import ToolMessage
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                )

        iterations += 1

    return {
        "research_data": research_data,
        "current_agent": "supervisor",
    }
