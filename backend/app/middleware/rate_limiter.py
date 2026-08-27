from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.rate_limit_store import rate_limit_store

logger = logging.getLogger("snt_ai.middleware.rate_limiter")


def _get_client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        key = _get_client_key(request)
        if await rate_limit_store.is_exceeded(key, self.max_requests, self.window_seconds):
            logger.warning("Rate limit exceeded for %s on %s", key, request.url.path)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        return await call_next(request)


def rate_limit(max_requests: int = 30, window_seconds: int = 60):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                for v in kwargs.values():
                    if isinstance(v, Request):
                        request = v
                        break
            if request:
                key = f"route:{_get_client_key(request)}:{request.url.path}"
                if await rate_limit_store.is_exceeded(key, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded for this endpoint.",
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

