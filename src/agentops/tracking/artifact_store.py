import json
from pathlib import Path
import tempfile

import mlflow

from agentops.observability.logger import get_logger

logger = get_logger("tracking.artifacts")


class ArtifactStore:
    """Manages MLflow artifacts for pipeline runs."""

    def log_research_data(self, research_data: list[dict]) -> None:
        """Log research data as a JSON artifact."""
        mlflow.log_text(json.dumps(research_data, indent=2), "research_data.json")

    def log_fact_checks(self, fact_checks: list[dict]) -> None:
        """Log fact check results as a JSON artifact."""
        mlflow.log_text(json.dumps(fact_checks, indent=2), "fact_checks.json")

    def log_guardrail_results(self, violations: list[dict]) -> None:
        """Log guardrail violations as a JSON artifact."""
        mlflow.log_text(json.dumps(violations, indent=2), "guardrail_violations.json")

    def log_evaluation_details(self, evaluations: list[dict]) -> None:
        """Log detailed evaluation results."""
        mlflow.log_text(json.dumps(evaluations, indent=2), "evaluations.json")

    def log_step_trace(self, steps: list[dict]) -> None:
        """Log the full execution trace of agent steps."""
        mlflow.log_text(json.dumps(steps, indent=2), "execution_trace.json")
