from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

import clickhouse_connect
from clickhouse_connect.driver.exceptions import DatabaseError, OperationalError

from app.config import get_config

logger = logging.getLogger("snt_ai.clickhouse")

config = get_config()


class ClickHouseManager:
    """
    Async ClickHouse client using clickhouse-connect.

    clickhouse_connect.aio.Client is natively async over HTTP — no
    asyncio.to_thread wrapping required.  The public interface matches
    the previous clickhouse-driver wrapper so all callers are unchanged.
    """

    def __init__(self) -> None:
        self._client: clickhouse_connect.driver.AsyncClient | None = None

    @property
    def client(self) -> clickhouse_connect.driver.AsyncClient:
        if self._client is None:
            raise RuntimeError("ClickHouse client not initialized. Call connect() first.")
        return self._client

    async def connect(self) -> None:
        if self._client is not None:
            return
        try:
            self._client = await clickhouse_connect.get_async_client(
                host=config.clickhouse_host,
                port=config.clickhouse_port,
                username=config.clickhouse_user,
                password=config.clickhouse_password,
                database=config.clickhouse_database,
            )
            logger.info(
                "ClickHouse async client configured for %s:%s",
                config.clickhouse_host,
                config.clickhouse_port,
            )
        except Exception as exc:
            logger.error("Failed to configure ClickHouse client: %s", exc)
            raise

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> list[tuple]:
        """Execute a query and return rows as a list of tuples."""
        try:
            result = await self.client.query(query, parameters=params or {})
            return result.result_rows  # type: ignore[return-value]
        except (DatabaseError, OperationalError) as exc:
            logger.error("ClickHouse query failed: %s | Query: %s", exc, query[:200])
            raise

    async def execute_batch(self, query: str, params: list[dict[str, Any]]) -> None:
        """Batch-insert rows via clickhouse-connect's native insert."""
        try:
            # clickhouse-connect insert: table name is parsed from the query
            # For INSERT INTO <table> VALUES, use raw_query
            await self.client.raw_query(query, parameters=params)
        except (DatabaseError, OperationalError) as exc:
            logger.error("ClickHouse batch insert failed: %s", exc)
            raise

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception as exc:
                logger.warning("Error closing ClickHouse client: %s", exc)
            finally:
                self._client = None

    async def health_check(self) -> bool:
        if self._client is None:
            return False
        try:
            return await self._client.ping()
        except Exception:
            return False


clickhouse_mgr = ClickHouseManager()


@asynccontextmanager
async def get_clickhouse():
    yield clickhouse_mgr
