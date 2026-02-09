"""Evaluation pipelines: LLM-as-judge scoring, A/B testing, ground truth comparison."""

from agentops.evaluation.ab_testing import ABTestManager
from agentops.evaluation.engine import EvaluationEngine

__all__ = ["EvaluationEngine", "ABTestManager"]
