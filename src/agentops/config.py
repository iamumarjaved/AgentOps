from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://agentops:agentops@localhost:5432/agentops"
    database_url_sync: str = "postgresql://agentops:agentops@localhost:5432/agentops"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI
    openai_api_key: str = ""

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Cost limits
    max_cost_per_run_usd: float = Field(default=5.00)
    max_tokens_per_run: int = Field(default=100_000)

    # Rate limiting
    rate_limit_requests_per_minute: int = 60

    @property
    def is_production(self) -> bool:
        return self.api_env == "production"


settings = Settings()
