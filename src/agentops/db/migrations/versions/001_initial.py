"""Initial schema

Revision ID: 001
Revises: None
Create Date: 2024-01-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # API Keys
    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("key_prefix", sa.String(10), nullable=False),
        sa.Column("scopes", JSONB, nullable=False, server_default="[]"),
        sa.Column("rate_limit", sa.Integer, nullable=False, server_default="60"),
        sa.Column("cost_limit_usd", sa.Float, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])

    # A/B Tests
    op.create_table(
        "ab_tests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("variants", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Runs
    run_status = sa.Enum("pending", "running", "completed", "failed", "cancelled", name="run_status")
    op.create_table(
        "runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("topic", sa.Text, nullable=False),
        sa.Column("config", JSONB, nullable=False, server_default="{}"),
        sa.Column("status", run_status, nullable=False, server_default="pending"),
        sa.Column("result", sa.Text, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cost_usd", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_latency_seconds", sa.Float, nullable=False, server_default="0"),
        sa.Column("mlflow_run_id", sa.String(64), nullable=True),
        sa.Column("ab_test_id", UUID(as_uuid=True), sa.ForeignKey("ab_tests.id"), nullable=True),
        sa.Column("variant", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_runs_status_created", "runs", ["status", "created_at"])

    # Agent Steps
    step_status = sa.Enum("pending", "running", "completed", "failed", name="step_status")
    op.create_table(
        "agent_steps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("step_order", sa.Integer, nullable=False),
        sa.Column("status", step_status, nullable=False, server_default="pending"),
        sa.Column("input_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float, nullable=False, server_default="0"),
        sa.Column("latency_seconds", sa.Float, nullable=False, server_default="0"),
        sa.Column("input_data", JSONB, nullable=True),
        sa.Column("output_data", JSONB, nullable=True),
        sa.Column("tool_calls", JSONB, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_agent_steps_run_id_order", "agent_steps", ["run_id", "step_order"])

    # Guardrail Violations
    guard_direction = sa.Enum("input", "output", name="guard_direction")
    guard_action = sa.Enum("blocked", "flagged", "sanitized", name="guard_action")
    guard_severity = sa.Enum("low", "medium", "high", "critical", name="guard_severity")
    op.create_table(
        "guardrail_violations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=True),
        sa.Column("guard_type", sa.String(100), nullable=False),
        sa.Column("direction", guard_direction, nullable=False),
        sa.Column("action", guard_action, nullable=False),
        sa.Column("severity", guard_severity, nullable=False),
        sa.Column("details", JSONB, nullable=False, server_default="{}"),
        sa.Column("original_content", sa.Text, nullable=True),
        sa.Column("sanitized_content", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_violations_type_created", "guardrail_violations", ["guard_type", "created_at"])

    # Evaluation Results
    op.create_table(
        "evaluation_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", UUID(as_uuid=True), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scorer_name", sa.String(100), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Ground Truths
    op.create_table(
        "ground_truths",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("topic", sa.Text, nullable=False),
        sa.Column("expected_output", sa.Text, nullable=False),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ground_truths_topic", "ground_truths", ["topic"])


def downgrade() -> None:
    op.drop_table("ground_truths")
    op.drop_table("evaluation_results")
    op.drop_table("guardrail_violations")
    op.drop_table("agent_steps")
    op.drop_table("runs")
    op.drop_table("ab_tests")
    op.drop_table("api_keys")
    sa.Enum(name="run_status").drop(op.get_bind())
    sa.Enum(name="step_status").drop(op.get_bind())
    sa.Enum(name="guard_direction").drop(op.get_bind())
    sa.Enum(name="guard_action").drop(op.get_bind())
    sa.Enum(name="guard_severity").drop(op.get_bind())
