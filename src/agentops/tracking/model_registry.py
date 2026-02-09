import json

import mlflow

from agentops.config import settings
from agentops.observability.logger import get_logger

logger = get_logger("tracking.registry")


class PromptRegistry:
    """Manages prompt templates via MLflow model registry."""

    REGISTRY_NAME = "agentops-prompts"

    def __init__(self):
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    def register_prompts(self, prompts: dict[str, str], version_tag: str = "latest") -> None:
        """Register prompt templates as a versioned artifact."""
        try:
            mlflow.set_experiment("agentops-prompts")
            with mlflow.start_run(run_name=f"prompts-{version_tag}"):
                mlflow.log_text(json.dumps(prompts, indent=2), "prompts.json")
                mlflow.set_tag("version", version_tag)

            logger.info("prompts_registered", version=version_tag, count=len(prompts))
        except Exception as e:
            logger.error("prompt_registration_failed", error=str(e))

    def get_prompts(self, version_tag: str = "latest") -> dict[str, str] | None:
        """Retrieve prompt templates by version. Returns None if not found."""
        try:
            experiment = mlflow.get_experiment_by_name("agentops-prompts")
            if not experiment:
                return None

            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"tags.version = '{version_tag}'",
                max_results=1,
            )

            if runs.empty:
                return None

            run_id = runs.iloc[0]["run_id"]
            artifact_path = mlflow.artifacts.download_artifacts(
                run_id=run_id, artifact_path="prompts.json"
            )

            with open(artifact_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error("prompt_retrieval_failed", error=str(e))
            return None
