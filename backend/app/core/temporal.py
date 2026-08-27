from __future__ import annotations

import logging
from typing import Any

from temporalio.client import Client

from app.config import get_config

logger = logging.getLogger("snt_ai.core.temporal")

_temporal_client: Client | None = None


async def init_temporal_client() -> Client | None:
    global _temporal_client
    if _temporal_client is not None:
        return _temporal_client

    config = get_config()
    try:
        _temporal_client = await Client.connect(
            config.temporal_host,
            namespace=config.temporal_namespace,
        )
        logger.info(
            "Connected to Temporal server at %s (namespace=%s)",
            config.temporal_host,
            config.temporal_namespace,
        )
    except Exception as exc:
        logger.warning(
            "Failed to connect to Temporal at %s — evaluations will run locally: %s",
            config.temporal_host,
            exc,
        )
        _temporal_client = None

    return _temporal_client


async def close_temporal_client() -> None:
    global _temporal_client
    if _temporal_client is not None:
        _temporal_client = None
        logger.info("Temporal client closed")


def get_temporal_client() -> Client | None:
    return _temporal_client
