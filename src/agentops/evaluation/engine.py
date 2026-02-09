from agentops.evaluation.scorers.accuracy import AccuracyScorer
from agentops.evaluation.scorers.completeness import CompletenessScorer
from agentops.evaluation.scorers.relevance import RelevanceScorer
from agentops.observability.logger import get_logger
from agentops.observability.metrics import evaluation_scores

logger = get_logger("evaluation.engine")

SCORER_MAP = {
    "relevance": RelevanceScorer,
    "accuracy": AccuracyScorer,
    "completeness": CompletenessScorer,
}


class EvaluationEngine:
    """Orchestrates evaluation scoring for completed runs."""

    async def evaluate(
        self,
        run_id: str,
        topic: str,
        report: str,
        scorers: list[str] | None = None,
    ) -> list[dict]:
        """Run specified scorers against a report."""
        scorer_names = scorers or list(SCORER_MAP.keys())
        results = []

        for name in scorer_names:
            scorer_cls = SCORER_MAP.get(name)
            if not scorer_cls:
                logger.warning("unknown_scorer", scorer=name)
                continue

            try:
                scorer = scorer_cls()
                result = await scorer.score(topic=topic, report=report)
                results.append(result)

                evaluation_scores.labels(scorer_name=name).observe(result["score"])
                logger.info(
                    "evaluation_scored",
                    run_id=run_id,
                    scorer=name,
                    score=result["score"],
                )
            except Exception as e:
                logger.error("evaluation_error", run_id=run_id, scorer=name, error=str(e))
                results.append({
                    "scorer": name,
                    "score": 0.0,
                    "reasoning": f"Error: {str(e)}",
                })

        return results
