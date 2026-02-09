import pytest

from agentops.evaluation.ab_testing import ABTestManager


class TestABTestManager:
    def setup_method(self):
        self.manager = ABTestManager()

    def test_assign_variant(self):
        variants = [
            {"name": "control", "weight": 0.5, "config": {"model": "gpt-4o"}},
            {"name": "treatment", "weight": 0.5, "config": {"model": "gpt-4o-mini"}},
        ]
        assignment = self.manager.assign_variant(variants)
        assert assignment.variant_name in ("control", "treatment")
        assert "model" in assignment.config

    def test_assign_variant_respects_weights(self):
        variants = [
            {"name": "control", "weight": 1.0, "config": {}},
            {"name": "treatment", "weight": 0.0, "config": {}},
        ]
        # With weight 0, should always be control
        assignments = [self.manager.assign_variant(variants) for _ in range(10)]
        assert all(a.variant_name == "control" for a in assignments)

    def test_compare_variants(self):
        a_scores = [0.8, 0.85, 0.9, 0.75]
        b_scores = [0.9, 0.92, 0.88, 0.95]

        result = ABTestManager.compare_variants(a_scores, b_scores)
        assert result["variant_a_mean"] > 0
        assert result["variant_b_mean"] > 0
        assert "improvement_pct" in result
        assert "recommended" in result

    def test_compare_empty_variants(self):
        result = ABTestManager.compare_variants([], [0.8])
        assert "error" in result
