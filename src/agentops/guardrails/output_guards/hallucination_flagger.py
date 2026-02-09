import json

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agentops.observability.logger import get_logger

logger = get_logger("guardrails.hallucination")


class HallucinationFlagger:
    """Flags potential hallucinations by checking output against source material."""

    async def check(self, output: str, source_material: str) -> dict:
        """Check output for potential hallucinations against source material."""
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        prompt = f"""Analyze the following output for potential hallucinations by comparing
it against the source material. Respond in JSON format.

Source Material:
{source_material[:4000]}

Output to Check:
{output[:2000]}

Respond with:
{{
    "has_hallucinations": true/false,
    "confidence": 0.0-1.0,
    "flagged_claims": [
        {{"claim": "...", "reason": "...", "severity": "low/medium/high"}}
    ]
}}"""

        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            result = json.loads(response.content)

            if result.get("has_hallucinations"):
                logger.warning(
                    "hallucination_flagged",
                    count=len(result.get("flagged_claims", [])),
                    confidence=result.get("confidence"),
                )

            return result
        except Exception as e:
            logger.error("hallucination_check_error", error=str(e))
            return {"has_hallucinations": False, "error": str(e)}
