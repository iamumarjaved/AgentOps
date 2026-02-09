import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set test environment variables
os.environ.setdefault("API_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://agentops:agentops@localhost:5432/agentops_test")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql://agentops:agentops@localhost:5432/agentops_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
