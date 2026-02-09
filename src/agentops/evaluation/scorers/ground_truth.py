import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class GroundTruthScorer:
    """Scores report against ground truth expected output using LLM-as-judge."""

    async def score(self, report: str, expected: str) -> dict:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        prompt = f"""Compare the generated report against the expected output.

Expected Output:
{expected[:3000]}

Generated Report:
{report[:3000]}

Score the similarity from 0.0 to 1.0 where:
- 1.0 = Covers all the same key points as expected
- 0.5 = Covers about half the key points
- 0.0 = Completely different content

Respond with JSON: {{"score": 0.0-1.0, "reasoning": "explanation", "matched_points": ["..."], "missed_points": ["..."]}}"""

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        try:
            result = json.loads(response.content)
            return {
                "scorer": "ground_truth",
                "score": min(max(float(result.get("score", 0)), 0), 1),
                "reasoning": result.get("reasoning", ""),
                "metadata": {
                    "matched_points": result.get("matched_points", []),
                    "missed_points": result.get("missed_points", []),
                },
            }
        except (json.JSONDecodeError, ValueError):
            return {"scorer": "ground_truth", "score": 0.5, "reasoning": "Failed to parse score"}
