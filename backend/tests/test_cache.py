from __future__ import annotations

import json

from app.core.cache import CacheService


class TestCacheService:
    def setup_method(self) -> None:
        self.cache = CacheService()

    def test_initial_state(self) -> None:
        assert self.cache._client is None
        assert self.cache._enabled is False
        assert self.cache.is_healthy is False

    async def test_get_returns_none_when_disabled(self) -> None:
        result = await self.cache.get("test-key")
        assert result is None

    async def test_set_does_not_raise_when_disabled(self) -> None:
        await self.cache.set("test-key", {"data": 123})

    async def test_delete_does_not_raise_when_disabled(self) -> None:
        await self.cache.delete("test-key")

    async def test_invalidate_pattern_does_not_raise_when_disabled(self) -> None:
        await self.cache.invalidate_pattern("test:*")

    async def test_initialize_does_not_raise(self) -> None:
        await self.cache.initialize()

    async def test_close_does_not_raise(self) -> None:
        await self.cache.close()
