from __future__ import annotations

import pytest

from app.core.rate_limit_store import rate_limit_store


class TestRateLimiter:
    def setup_method(self) -> None:
        rate_limit_store._fallback.clear()

    @pytest.mark.asyncio
    async def test_rate_limit_not_exceeded(self) -> None:
        key = "test-client"
        assert await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=60) is False

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self) -> None:
        key = "test-client-exceeded"
        for _ in range(5):
            await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=60)
        assert await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=60) is True

    @pytest.mark.asyncio
    async def test_rate_limit_resets_after_window(self) -> None:
        key = "test-client-reset"
        for _ in range(5):
            await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=1)
        assert await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=1) is True

    @pytest.mark.asyncio
    async def test_rate_limit_just_under(self) -> None:
        key = "test-client-under"
        for _ in range(4):
            await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=60)
        assert await rate_limit_store.is_exceeded(key, max_requests=5, window_seconds=60) is False

    @pytest.mark.asyncio
    async def test_multiple_keys_independent(self) -> None:
        for _ in range(3):
            await rate_limit_store.is_exceeded("key-a", max_requests=3, window_seconds=60)
        for _ in range(2):
            await rate_limit_store.is_exceeded("key-b", max_requests=3, window_seconds=60)
        assert await rate_limit_store.is_exceeded("key-a", max_requests=3, window_seconds=60) is True
        assert await rate_limit_store.is_exceeded("key-b", max_requests=3, window_seconds=60) is False

    @pytest.mark.asyncio
    async def test_empty_window_clears_stale(self) -> None:
        import time
        key = "test-stale"
        rate_limit_store._fallback[key] = [time.time() - 120, time.time() - 120]
        result = await rate_limit_store.is_exceeded(key, max_requests=1, window_seconds=60)
        assert result is False
        assert len(rate_limit_store._fallback[key]) == 1
