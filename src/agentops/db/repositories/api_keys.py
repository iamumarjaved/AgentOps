from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentops.db.models import APIKey


class APIKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, key_hash: str, key_prefix: str,
                     scopes: list[str] | None = None, rate_limit: int = 60,
                     cost_limit_usd: float | None = None) -> APIKey:
        api_key = APIKey(
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=scopes or ["runs:read", "runs:write"],
            rate_limit=rate_limit,
            cost_limit_usd=cost_limit_usd,
        )
        self.session.add(api_key)
        await self.session.flush()
        return api_key

    async def get_by_hash(self, key_hash: str) -> APIKey | None:
        result = await self.session.execute(
            select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def update_last_used(self, key_hash: str) -> None:
        result = await self.session.execute(
            select(APIKey).where(APIKey.key_hash == key_hash)
        )
        api_key = result.scalar_one_or_none()
        if api_key:
            api_key.last_used_at = datetime.utcnow()
