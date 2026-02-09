from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    topic: str = Field(..., min_length=3, max_length=5000, description="Research topic")
    config: dict = Field(default_factory=dict, description="Optional pipeline configuration")


class EvaluationTrigger(BaseModel):
    run_id: str = Field(..., description="Run ID to evaluate")
    scorers: list[str] = Field(
        default=["relevance", "accuracy", "completeness"],
        description="Scorers to run",
    )


class GuardrailCheck(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    direction: str = Field(default="input", pattern="^(input|output)$")
