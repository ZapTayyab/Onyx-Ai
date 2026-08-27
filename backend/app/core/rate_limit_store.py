from __future__ import annotations

import logging
from typing import Any

from app.core.cache import cache_service

logger = logging.getLogger("snt_ai.core.rate_limit_store")

_REDIS_KEY_PREFIX = "rl:"


class RedisRateLimitStore:
    """
    Atomic sliding-window rate-limit counter backed by Redis.

    Uses INCR + EXPIRE so the window resets cleanly even across
    multiple processes / restarts.  Falls back to an in-memory
    defaultdict if Redis is unavailable (e.g. during tests).
    """

    def __init__(self) -> None:
        from collections import defaultdict
        self._fallback: dict[str, list[float]] = defaultdict(list)

    async def is_exceeded(self, key: str, max_requests: int, window_seconds: int) -> bool:
        redis = getattr(cache_service, "_client", None)
        if redis is None:
            return self._fallback_check(key, max_requests, window_seconds)

        try:
            redis_key = f"{_REDIS_KEY_PREFIX}{key}:{window_seconds}"
            count = await redis.incr(redis_key)
            if count == 1:
                # First hit in this window — set TTL
                await redis.expire(redis_key, window_seconds)
            return count > max_requests
        except Exception as exc:
            logger.warning("Redis rate-limit unavailable, using fallback: %s", exc)
            return self._fallback_check(key, max_requests, window_seconds)

    # ------------------------------------------------------------------
    # In-process fallback (sliding window list)
    # ------------------------------------------------------------------

    def _fallback_check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        import time
        now = time.time()
        window_start = now - window_seconds
        timestamps = self._fallback[key]
        self._fallback[key] = [t for t in timestamps if t > window_start]
        if len(self._fallback[key]) >= max_requests:
            return True
        self._fallback[key].append(now)
        return False


# Shared singleton — imported by rate_limiter middleware and decorator
rate_limit_store = RedisRateLimitStore()
