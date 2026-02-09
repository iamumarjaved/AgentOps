import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.db.engine import get_session
from agentops.db.repositories.api_keys import APIKeyRepository

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_api_key(key: str) -> str:
    """Hash API key using SHA-256 for lookup."""
    return hashlib.sha256(key.encode()).hexdigest()


async def get_api_key(
    api_key: str | None = Security(api_key_header),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Validate API key and return key info."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    key_hash = hash_api_key(api_key)
    repo = APIKeyRepository(session)
    db_key = await repo.get_by_hash(key_hash)

    if not db_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    await repo.update_last_used(key_hash)
    await session.commit()

    return {
        "id": str(db_key.id),
        "name": db_key.name,
        "scopes": db_key.scopes,
        "rate_limit": db_key.rate_limit,
        "cost_limit_usd": db_key.cost_limit_usd,
    }


AuthDep = Annotated[dict, Depends(get_api_key)]
