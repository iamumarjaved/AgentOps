import random
from dataclasses import dataclass

from agentops.observability.logger import get_logger

logger = get_logger("evaluation.ab_testing")


@dataclass
class VariantAssignment:
    variant_name: str
    config: dict


class ABTestManager:
    """Manages A/B test variant assignment and comparison."""

    def assign_variant(self, variants: list[dict]) -> VariantAssignment:
        """Assign a variant based on weights."""
        weights = [v.get("weight", 1.0) for v in variants]
        total = sum(weights)
        normalized = [w / total for w in weights]

        choice = random.random()
        cumulative = 0.0

        for i, weight in enumerate(normalized):
            cumulative += weight
            if choice <= cumulative:
                variant = variants[i]
                return VariantAssignment(
                    variant_name=variant["name"],
                    config=variant.get("config", {}),
                )

        # Fallback to last variant
        variant = variants[-1]
        return VariantAssignment(variant_name=variant["name"], config=variant.get("config", {}))

    @staticmethod
    def compare_variants(
        variant_a_scores: list[float], variant_b_scores: list[float]
    ) -> dict:
        """Compare two variants statistically."""
        if not variant_a_scores or not variant_b_scores:
            return {"error": "Insufficient data for comparison"}

        mean_a = sum(variant_a_scores) / len(variant_a_scores)
        mean_b = sum(variant_b_scores) / len(variant_b_scores)

        improvement = ((mean_b - mean_a) / mean_a * 100) if mean_a > 0 else 0

        return {
            "variant_a_mean": round(mean_a, 4),
            "variant_b_mean": round(mean_b, 4),
            "improvement_pct": round(improvement, 2),
            "variant_a_count": len(variant_a_scores),
            "variant_b_count": len(variant_b_scores),
            "recommended": "variant_b" if mean_b > mean_a else "variant_a",
        }
