from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
    research_data: list[dict]
    summary: str
    fact_check_results: list[dict]
    report: str
    current_agent: str
    step_count: int
    metadata: dict
