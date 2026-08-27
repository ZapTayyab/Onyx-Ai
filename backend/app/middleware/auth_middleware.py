from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.database import _get_session_factory
from app.core.logging import request_id_var, org_id_var, user_id_var
from app.core.security import verify_token
from app.models.postgres import Organization as OrganizationModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("snt_ai.middleware.auth")


class OrganizationContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        public_paths = {"/docs", "/redoc", "/openapi.json", "/health", "/auth/me"}

        if request.url.path in public_paths or request.url.path.startswith(("/auth/login", "/health")):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
                payload = await verify_token(credentials)
                
                import uuid
                factory = _get_session_factory()
                async with factory() as db:
                    org_res = await db.execute(select(OrganizationModel).where(OrganizationModel.id == uuid.UUID(str(payload.org_id))))
                    org = org_res.scalar_one_or_none()
                    if org and org.settings:
                        settings = json.loads(org.settings) if isinstance(org.settings, str) else org.settings
                        if settings.get("sso_enabled") and payload.sub.startswith("dev:"):
                            return JSONResponse(
                                status_code=status.HTTP_403_FORBIDDEN,
                                content={"detail": "SSO is enforced for this organization. Local tokens are not allowed."},
                            )

                org_id_var.set(str(payload.org_id))
                user_id_var.set(str(payload.sub))
                request.state.user_payload = payload
            except Exception as exc:
                logger.warning("Auth middleware: token verification failed: %s", exc)

        response = await call_next(request)
        return response
