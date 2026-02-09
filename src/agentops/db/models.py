import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    key_prefix = Column(String(10), nullable=False)
    scopes = Column(JSONB, nullable=False, default=list)
    rate_limit = Column(Integer, nullable=False, default=60)
    cost_limit_usd = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)


class Run(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False)
    config = Column(JSONB, nullable=False, default=dict)
    status = Column(
        Enum("pending", "running", "completed", "failed", "cancelled", name="run_status"),
        nullable=False,
        default="pending",
    )
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

    # Aggregate metrics
    total_tokens = Column(Integer, nullable=False, default=0)
    total_cost_usd = Column(Float, nullable=False, default=0.0)
    total_latency_seconds = Column(Float, nullable=False, default=0.0)

    # MLflow reference
    mlflow_run_id = Column(String(64), nullable=True)

    # A/B testing
    ab_test_id = Column(UUID(as_uuid=True), ForeignKey("ab_tests.id"), nullable=True)
    variant = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    steps = relationship("AgentStep", back_populates="run", cascade="all, delete-orphan")
    violations = relationship(
        "GuardrailViolation", back_populates="run", cascade="all, delete-orphan"
    )
    evaluation_results = relationship(
        "EvaluationResult", back_populates="run", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_runs_status_created", "status", "created_at"),
    )


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    step_order = Column(Integer, nullable=False)
    status = Column(
        Enum("pending", "running", "completed", "failed", name="step_status"),
        nullable=False,
        default="pending",
    )

    # Token tracking
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)

    # Latency
    latency_seconds = Column(Float, nullable=False, default=0.0)

    # I/O data
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    tool_calls = Column(JSONB, nullable=True)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    run = relationship("Run", back_populates="steps")

    __table_args__ = (
        Index("ix_agent_steps_run_id_order", "run_id", "step_order"),
    )


class GuardrailViolation(Base):
    __tablename__ = "guardrail_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=True)
    guard_type = Column(String(100), nullable=False)
    direction = Column(
        Enum("input", "output", name="guard_direction"), nullable=False
    )
    action = Column(
        Enum("blocked", "flagged", "sanitized", name="guard_action"), nullable=False
    )
    severity = Column(
        Enum("low", "medium", "high", "critical", name="guard_severity"), nullable=False
    )
    details = Column(JSONB, nullable=False, default=dict)
    original_content = Column(Text, nullable=True)
    sanitized_content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    run = relationship("Run", back_populates="violations")

    __table_args__ = (
        Index("ix_violations_type_created", "guard_type", "created_at"),
    )


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    scorer_name = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    run = relationship("Run", back_populates="evaluation_results")


class ABTest(Base):
    __tablename__ = "ab_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    variants = Column(JSONB, nullable=False)  # [{"name": "control", "weight": 0.5, "config": {}}]
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class GroundTruth(Base):
    __tablename__ = "ground_truths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False, index=True)
    expected_output = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
