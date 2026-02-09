"""Generate an API key for the AgentOps platform."""
import asyncio
import hashlib
import secrets
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Add src to path for imports
sys.path.insert(0, "src")

from agentops.config import settings
from agentops.db.models import APIKey, Base


def generate_api_key(name: str = "default") -> tuple[str, str]:
    """Generate a new API key and store its hash in the database."""
    raw_key = f"agentops_{secrets.token_hex(24)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:14]

    engine = create_engine(settings.database_url_sync)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        api_key = APIKey(
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=["runs:read", "runs:write", "evaluations:read", "evaluations:write"],
            rate_limit=60,
        )
        session.add(api_key)
        session.commit()

    return raw_key, key_prefix


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "default"
    key, prefix = generate_api_key(name)
    print(f"API Key generated successfully!")
    print(f"  Name:   {name}")
    print(f"  Prefix: {prefix}")
    print(f"  Key:    {key}")
    print(f"\nStore this key securely — it cannot be retrieved later.")
