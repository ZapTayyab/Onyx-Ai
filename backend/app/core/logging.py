from __future__ import annotations

import logging
import sys
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from app.config import get_config

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
org_id_var: ContextVar[str] = ContextVar("org_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        if hasattr(record, "structured") and record.structured:
            import json

            log_entry: dict[str, Any] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "request_id": request_id_var.get(),
                "org_id": org_id_var.get(),
                "user_id": user_id_var.get(),
            }
            if hasattr(record, "extra_fields"):
                log_entry.update(record.extra_fields)
            if record.exc_info and record.exc_info[0]:
                log_entry["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_entry)
        return base


def configure_logging() -> None:
    config = get_config()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger("snt_ai")
    root_logger.setLevel(config.log_level.upper())
    root_logger.addHandler(handler)
    root_logger.propagate = False

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(handler)

    if config.is_development:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.WARN)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"snt_ai.{name}")


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **extra_fields: Any,
) -> None:
    logger.log(level, message, extra={"structured": True, "extra_fields": extra_fields})


class RequestContextMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    async def __call__(self, request: Any) -> Any:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        org_id_var.set(request.headers.get("X-Org-ID", ""))
        user_id_var.set(request.headers.get("X-User-ID", ""))
        response = await self.get_response(request)
        response.headers["X-Request-ID"] = request_id
        return response
