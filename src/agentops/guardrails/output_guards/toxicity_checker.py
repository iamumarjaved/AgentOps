import httpx

from agentops.config import settings
from agentops.observability.logger import get_logger

logger = get_logger("guardrails.toxicity")


class ToxicityChecker:
    """Checks output text for toxic content using OpenAI Moderation API."""

    CATEGORY_THRESHOLDS = {
        "hate": 0.5,
        "hate/threatening": 0.3,
        "harassment": 0.5,
        "harassment/threatening": 0.3,
        "self-harm": 0.3,
        "sexual": 0.5,
        "violence": 0.5,
    }

    async def check(self, text: str) -> dict:
        """Check text for toxic content."""
        if not settings.openai_api_key:
            return {"is_toxic": False, "categories": {}, "error": "No API key configured"}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    "https://api.openai.com/v1/moderations",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    json={"input": text},
                )
                response.raise_for_status()
                data = response.json()

            result = data["results"][0]
            flagged_categories = {}

            for category, score in result.get("category_scores", {}).items():
                threshold = self.CATEGORY_THRESHOLDS.get(category, 0.5)
                if score >= threshold:
                    flagged_categories[category] = round(score, 4)

            if flagged_categories:
                logger.warning("toxicity_detected", categories=flagged_categories)

            return {
                "is_toxic": bool(flagged_categories),
                "categories": flagged_categories,
                "flagged": result.get("flagged", False),
            }
        except Exception as e:
            logger.error("toxicity_check_error", error=str(e))
            return {"is_toxic": False, "categories": {}, "error": str(e)}
