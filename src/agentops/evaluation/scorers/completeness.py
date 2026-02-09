import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class CompletenessScorer:
    """Scores how complete and thorough the report is."""

    async def score(self, topic: str, report: str) -> dict:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        prompt = f"""Evaluate the completeness of this report.

Topic: {topic}

Report:
{report[:4000]}

Score from 0.0 to 1.0 where:
- 1.0 = Comprehensive, covers all important aspects
- 0.5 = Covers basics but missing important details
- 0.0 = Very incomplete, major gaps

Consider:
- Does it cover multiple perspectives?
- Are key subtopics addressed?
- Is there sufficient depth of analysis?
- Are conclusions supported by evidence?

Respond with JSON: {{"score": 0.0-1.0, "reasoning": "explanation"}}"""

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        try:
            result = json.loads(response.content)
            return {
                "scorer": "completeness",
                "score": min(max(float(result.get("score", 0)), 0), 1),
                "reasoning": result.get("reasoning", ""),
            }
        except (json.JSONDecodeError, ValueError):
            return {"scorer": "completeness", "score": 0.5, "reasoning": "Failed to parse score"}
