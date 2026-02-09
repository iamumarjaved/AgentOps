import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class RelevanceScorer:
    """Scores how relevant the report is to the original topic."""

    async def score(self, topic: str, report: str) -> dict:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        prompt = f"""Score the relevance of this report to the given topic.

Topic: {topic}

Report:
{report[:4000]}

Score from 0.0 to 1.0 where:
- 1.0 = Perfectly relevant, directly addresses the topic
- 0.5 = Partially relevant, some off-topic content
- 0.0 = Completely irrelevant

Respond with JSON: {{"score": 0.0-1.0, "reasoning": "explanation"}}"""

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        try:
            result = json.loads(response.content)
            return {
                "scorer": "relevance",
                "score": min(max(float(result.get("score", 0)), 0), 1),
                "reasoning": result.get("reasoning", ""),
            }
        except (json.JSONDecodeError, ValueError):
            return {"scorer": "relevance", "score": 0.5, "reasoning": "Failed to parse score"}
