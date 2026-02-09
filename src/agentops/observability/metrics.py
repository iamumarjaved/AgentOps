from prometheus_client import Counter, Gauge, Histogram

# Run metrics
runs_total = Counter(
    "agentops_runs_total",
    "Total number of pipeline runs",
    ["status"],
)

active_runs = Gauge(
    "agentops_active_runs",
    "Currently executing runs",
)

run_latency_seconds = Histogram(
    "agentops_run_latency_seconds",
    "End-to-end run latency in seconds",
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

# Agent step metrics
agent_step_latency_seconds = Histogram(
    "agentops_agent_step_latency_seconds",
    "Per-agent step latency in seconds",
    ["agent_name"],
    buckets=[0.5, 1, 2, 5, 10, 30, 60],
)

# Token metrics
tokens_total = Counter(
    "agentops_tokens_total",
    "Total tokens used",
    ["agent_name", "direction"],
)

# Cost metrics
cost_usd_total = Counter(
    "agentops_cost_usd_total",
    "Total cost in USD",
    ["agent_name"],
)

# Guardrail metrics
guardrail_violations_total = Counter(
    "agentops_guardrail_violations_total",
    "Total guardrail violations",
    ["guard_type", "action"],
)

# Guardrail check latency
guardrail_check_latency = Histogram(
    "agentops_guardrail_check_latency_seconds",
    "Guardrail check latency",
    ["guard_type"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5],
)

# Evaluation metrics
evaluation_scores = Histogram(
    "agentops_evaluation_score",
    "Evaluation scores",
    ["scorer_name"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)
