import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class AccuracyScorer:
    """Scores the factual accuracy of the report."""

    async def score(self, topic: str, report: str) -> dict:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        prompt = f"""Evaluate the factual accuracy of this report.

Topic: {topic}

Report:
{report[:4000]}

Score from 0.0 to 1.0 where:
- 1.0 = All claims appear factually accurate
- 0.5 = Mix of accurate and questionable claims
- 0.0 = Major factual errors throughout

Consider:
- Are specific claims verifiable?
- Are statistics and data points plausible?
- Are sources properly attributed?

Respond with JSON: {{"score": 0.0-1.0, "reasoning": "explanation"}}"""

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        try:
            result = json.loads(response.content)
            return {
                "scorer": "accuracy",
                "score": min(max(float(result.get("score", 0)), 0), 1),
                "reasoning": result.get("reasoning", ""),
            }
        except (json.JSONDecodeError, ValueError):
            return {"scorer": "accuracy", "score": 0.5, "reasoning": "Failed to parse score"}
