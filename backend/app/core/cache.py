from __future__ import annotations

import json
import logging
from typing import Any

from app.config import get_config

logger = logging.getLogger("snt_ai.core.cache")

try:
    import redis.asyncio as aioredis

    _redis_available = True
except ImportError:
    _redis_available = False


class CacheService:
    def __init__(self) -> None:
        self._client: Any = None
        self._enabled = False

    async def initialize(self) -> None:
        if not _redis_available:
            logger.warning("redis not installed; cache disabled")
            return
        config = get_config()
        try:
            self._client = aioredis.from_url(str(config.redis_dsn), decode_responses=True)
            await self._client.ping()
            self._enabled = True
            logger.info("Cache connected to Redis at %s", config.redis_dsn)
        except Exception as exc:
            logger.warning("Cache unavailable (non-fatal): %s", exc)
            self._enabled = False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def get(self, key: str) -> Any | None:
        if not self._enabled:
            return None
        try:
            val = await self._client.get(key)
            if val:
                return json.loads(val)
        except Exception as exc:
            logger.debug("Cache get error: %s", exc)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        if not self._enabled:
            return
        try:
            await self._client.setex(key, ttl, json.dumps(value, default=str))
        except Exception as exc:
            logger.debug("Cache set error: %s", exc)

    async def delete(self, key: str) -> None:
        if not self._enabled:
            return
        try:
            await self._client.delete(key)
        except Exception as exc:
            logger.debug("Cache delete error: %s", exc)

    async def invalidate_pattern(self, pattern: str) -> None:
        if not self._enabled:
            return
        try:
            keys_to_delete = []
            async for key in self._client.scan_iter(match=pattern):
                keys_to_delete.append(key)
            if keys_to_delete:
                await self._client.delete(*keys_to_delete)
        except Exception as exc:
            logger.debug("Cache invalidate pattern error: %s", exc)

    @property
    def is_healthy(self) -> bool:
        return self._enabled


cache_service = CacheService()
