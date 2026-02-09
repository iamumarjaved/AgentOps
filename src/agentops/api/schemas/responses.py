from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
    environment: str


class ReadyResponse(BaseModel):
    status: str
    database: str
    redis: str


class RunResponse(BaseModel):
    id: UUID
    topic: str
    status: str
    config: dict
    total_tokens: int
    total_cost_usd: float
    total_latency_seconds: float
    variant: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class RunCreatedResponse(BaseModel):
    id: UUID
    status: str
    message: str


class AgentStepResponse(BaseModel):
    id: UUID
    agent_name: str
    step_order: int
    status: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    tool_calls: list | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class RunDetailResponse(RunResponse):
    result: str | None = None
    error: str | None = None
    steps: list[AgentStepResponse] = []


class ViolationResponse(BaseModel):
    id: UUID
    run_id: UUID | None = None
    guard_type: str
    direction: str
    action: str
    severity: str
    details: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationResultResponse(BaseModel):
    id: UUID
    run_id: UUID
    scorer_name: str
    score: float
    reasoning: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationSummaryResponse(BaseModel):
    average_scores: dict[str, float]
    total_evaluations: int


class CostMetricsResponse(BaseModel):
    total_cost_usd: float
    cost_by_agent: dict[str, float]
    cost_by_day: list[dict]


class TokenMetricsResponse(BaseModel):
    total_tokens: int
    tokens_by_agent: dict[str, dict[str, int]]


class LatencyMetricsResponse(BaseModel):
    average_latency_seconds: float
    p95_latency_seconds: float
    latency_by_agent: dict[str, float]
