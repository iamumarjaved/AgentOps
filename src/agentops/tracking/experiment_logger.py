import json

import mlflow

from agentops.config import settings
from agentops.observability.logger import get_logger

logger = get_logger("tracking.experiment")


class ExperimentLogger:
    """Logs experiment data to MLflow."""

    EXPERIMENT_NAME = "agentops-research-pipeline"

    def __init__(self):
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    def start_run(self, run_id: str, topic: str, config: dict) -> str:
        """Start an MLflow run and log parameters."""
        mlflow.set_experiment(self.EXPERIMENT_NAME)
        mlflow_run = mlflow.start_run(run_name=f"pipeline-{run_id[:8]}")

        mlflow.log_params({
            "run_id": run_id,
            "topic": topic[:250],
            "model": config.get("model", "gpt-4o"),
            "variant": config.get("variant", "default"),
        })

        return mlflow_run.info.run_id

    def log_step_metrics(self, agent_name: str, metrics: dict) -> None:
        """Log metrics for an agent step."""
        prefixed = {f"{agent_name}_{k}": v for k, v in metrics.items() if isinstance(v, (int, float))}
        mlflow.log_metrics(prefixed)

    def log_run_metrics(self, total_tokens: int, total_cost: float,
                        latency: float, status: str) -> None:
        """Log aggregate run metrics."""
        mlflow.log_metrics({
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "total_latency_seconds": latency,
        })
        mlflow.set_tag("status", status)

    def log_evaluation_scores(self, scores: dict[str, float]) -> None:
        """Log evaluation scores."""
        prefixed = {f"eval_{k}": v for k, v in scores.items()}
        mlflow.log_metrics(prefixed)

    def log_report_artifact(self, report: str, filename: str = "report.md") -> None:
        """Log the final report as an artifact."""
        mlflow.log_text(report, filename)

    def log_config_artifact(self, config: dict, filename: str = "config.json") -> None:
        """Log configuration as an artifact."""
        mlflow.log_text(json.dumps(config, indent=2), filename)

    def end_run(self) -> None:
        """End the current MLflow run."""
        mlflow.end_run()
