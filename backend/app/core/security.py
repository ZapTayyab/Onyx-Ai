from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import AppConfig, UserRole, get_config

logger = logging.getLogger("snt_ai.security")

security_scheme = HTTPBearer(auto_error=False)

AUDIT_LOG_EVENT = "snt_ai.auth.audit"


class TokenPayload(BaseModel):
    sub: str
    org_id: str
    role: UserRole
    email: str | None = None
    exp: datetime | None = None


class AuthAuditLog(BaseModel):
    event: str = AUDIT_LOG_EVENT
    user_id: str
    org_id: str
    action: str
    resource: str
    success: bool
    timestamp: str
    ip_address: str | None = None
    user_agent: str | None = None


class ClerkJWKSProvider:
    _jwks_client: dict[str, Any] | None = None
    _jwks_cache_until: datetime | None = None

    @classmethod
    async def get_jwks(cls, config: AppConfig) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        if cls._jwks_client is not None and cls._jwks_cache_until and now < cls._jwks_cache_until:
            return cls._jwks_client

        domain = config.clerk_secret_key.split("_")[-1] if "_" in config.clerk_secret_key else ""
        if not domain:
            jwks_url = "https://clerk.snt.ai/.well-known/jwks.json"
        else:
            jwks_url = f"https://{domain}.clerk.accounts.dev/.well-known/jwks.json"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(jwks_url, timeout=10)
                response.raise_for_status()
                cls._jwks_client = response.json()
                cls._jwks_cache_until = now + timedelta(hours=1)
                return cls._jwks_client
            except httpx.HTTPStatusError as exc:
                logger.error("Failed to fetch Clerk JWKS: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Authentication provider unreachable",
                )


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> TokenPayload:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    config = get_config()

    if config.auth_provider == "clerk":
        return await _verify_clerk_token(credentials.credentials, config)
    elif config.auth_provider == "auth0":
        return await _verify_auth0_token(credentials.credentials, config)
    elif config.auth_provider in ("local", "dev") or config.is_development:
        return await _verify_dev_token(credentials.credentials, config)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unsupported auth provider: {config.auth_provider}",
        )


async def _verify_dev_token(token: str, config: AppConfig) -> TokenPayload:
    try:
        secret = config.encryption_key
        if not secret or secret == "dev-secret-key-change-in-production":
            if config.is_production:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Insecure JWT secret configuration in production",
                )
            secret = "dev-secret-key-change-in-production"

        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )
        return TokenPayload(
            sub=payload.get("sub", ""),
            org_id=payload.get("org_id", ""),
            role=UserRole(payload.get("role", "member")),
            email=payload.get("email", None),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def _verify_clerk_token(token: str, config: AppConfig) -> TokenPayload:
    try:
        jwks = await ClerkJWKSProvider.get_jwks(config)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwks["keys"][0])
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return TokenPayload(
            sub=payload.get("sub", ""),
            org_id=payload.get("org_id", payload.get("orgs", [{}])[0].get("id", "")),
            role=_map_clerk_role(payload.get("org_role", "")),
            email=payload.get("email", None),
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def _verify_auth0_token(token: str, config: AppConfig) -> TokenPayload:
    try:
        jwks_url = f"https://{config.auth0_domain}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=config.auth0_audience,
            issuer=config.auth0_issuer,
        )
        return TokenPayload(
            sub=payload.get("sub", ""),
            org_id=payload.get(f"{config.auth0_domain}/org_id", ""),
            role=_map_auth0_role(payload.get(f"{config.auth0_domain}/roles", [])),
            email=payload.get("email", None),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def _map_clerk_role(org_role: str) -> UserRole:
    role_mapping = {
        "org:admin": UserRole.ADMIN,
        "org:member": UserRole.MEMBER,
        "org:viewer": UserRole.VIEWER,
    }
    return role_mapping.get(org_role, UserRole.VIEWER)


def _map_auth0_role(roles: list[str]) -> UserRole:
    if "admin" in roles:
        return UserRole.ADMIN
    if "member" in roles:
        return UserRole.MEMBER
    return UserRole.VIEWER


def require_role(required_role: UserRole):
    async def role_checker(payload: TokenPayload = Depends(verify_token)) -> TokenPayload:
        role_priority = {
            UserRole.VIEWER: 0,
            UserRole.MEMBER: 1,
            UserRole.ADMIN: 2,
        }
        if role_priority.get(payload.role, 0) < role_priority.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {payload.role} insufficient. Required: {required_role}",
            )
        return payload

    return role_checker


require_admin = require_role(UserRole.ADMIN)
require_member = require_role(UserRole.MEMBER)


def create_audit_log(
    user_id: str,
    org_id: str,
    action: str,
    resource: str,
    success: bool,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuthAuditLog:
    return AuthAuditLog(
        user_id=user_id,
        org_id=org_id,
        action=action,
        resource=resource,
        success=success,
        timestamp=datetime.now(timezone.utc).isoformat(),
        ip_address=ip_address,
        user_agent=user_agent,
    )
