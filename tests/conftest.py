"""Shared test configuration and fixtures."""

import os
import sys
from pathlib import Path

# Add src/ to Python path so `import agentops` resolves
_src_dir = str(Path(__file__).resolve().parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Set test environment variables (only if not already set by CI)
_test_env = {
    "API_ENV": "testing",
    "DATABASE_URL": "postgresql+asyncpg://agentops:agentops@localhost:5432/agentops_test",
    "DATABASE_URL_SYNC": "postgresql://agentops:agentops@localhost:5432/agentops_test",
    "REDIS_URL": "redis://localhost:6379/0",
    "OPENAI_API_KEY": "test-key",
    "CELERY_BROKER_URL": "redis://localhost:6379/1",
    "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
    "MLFLOW_TRACKING_URI": "http://localhost:5000",
    "SECRET_KEY": "test-secret-key",
    "MAX_COST_PER_RUN_USD": "5.00",
    "MAX_TOKENS_PER_RUN": "100000",
    "RATE_LIMIT_REQUESTS_PER_MINUTE": "60",
}

for key, value in _test_env.items():
    os.environ.setdefault(key, value)
