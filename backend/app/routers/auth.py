from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_config
from app.core.database import get_async_session
from app.core.security import AuthAuditLog, TokenPayload, create_audit_log, require_member, verify_token
from app.models.postgres import AuditLog as AuditLogModel
from app.models.postgres import Organization as OrganizationModel
from app.models.postgres import User as UserModel
from app.schemas.auth import AuthAuditLogResponse, TokenResponse, UserInfo
from sqlalchemy import desc

logger = logging.getLogger("snt_ai.routers.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    config = get_config()

    # DEV-ONLY backdoor — explicitly blocked in production regardless of any
    # other config to prevent accidental credential exposure.
    if config.is_development:
        if config.is_production:
            # This path should never be reachable, but belt-and-suspenders.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Dev login is disabled in production",
            )
        if body.email == "admin@snt.ai" and body.password == "admin":
            result = await db.execute(
                select(OrganizationModel).where(OrganizationModel.slug == "demo")
            )
            org = result.scalar_one_or_none()
            if org is None:
                org = OrganizationModel(name="Demo Organization", slug="demo")
                db.add(org)
                await db.flush()

            user_result = await db.execute(
                select(UserModel).where(UserModel.email == body.email)
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                user = UserModel(
                    organization_id=org.id,
                    email=body.email,
                    auth_provider_id=f"dev:{uuid.uuid4()}",
                    role="admin",
                )
                db.add(user)
                await db.flush()
                await db.refresh(user)

            secret = config.encryption_key
            if not secret or secret == "dev-secret-key-change-in-production":
                if config.is_production:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Insecure JWT secret configuration in production",
                    )
                secret = "dev-secret-key-change-in-production"

            token = jwt.encode(
                {
                    "sub": user.auth_provider_id,
                    "org_id": str(user.organization_id),
                    "role": user.role,
                    "email": user.email,
                    "exp": datetime.now(timezone.utc) + timedelta(hours=24),
                },
                secret,
                algorithm="HS256",
            )

            return TokenResponse(
                access_token=token,
                token_type="Bearer",
                expires_in=86400,
            )

    result = await db.execute(
        select(UserModel).where(UserModel.email == body.email)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    secret = config.encryption_key
    if not secret or secret == "dev-secret-key-change-in-production":
        if config.is_production:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Insecure JWT secret configuration in production",
            )
        secret = "dev-secret-key-change-in-production"

    token = jwt.encode(
        {
            "sub": user.auth_provider_id,
            "org_id": str(user.organization_id),
            "role": user.role,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        secret,
        algorithm="HS256",
    )

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=86400,
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user(
    payload: TokenPayload = Depends(verify_token),
    db: AsyncSession = Depends(get_async_session),
) -> UserInfo:
    result = await db.execute(
        select(UserModel).where(UserModel.auth_provider_id == payload.sub)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = UserModel(
            organization_id=payload.org_id,
            email=payload.email or "",
            auth_provider_id=payload.sub,
            role=payload.role,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    return UserInfo.model_validate(user)


@router.get("/audit-log", response_model=list[AuthAuditLogResponse])
async def get_audit_logs(
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 50,
) -> list[AuthAuditLogResponse]:
    result = await db.execute(
        select(AuditLogModel)
        .where(AuditLogModel.organization_id == payload.org_id)
        .order_by(desc(AuditLogModel.created_at))
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        AuthAuditLogResponse(
            user_id=r.user_id,
            org_id=str(r.organization_id),
            action=r.action,
            resource=r.resource,
            success=r.success,
            ip_address=r.ip_address,
            user_agent=r.user_agent,
            timestamp=r.created_at.isoformat(),
        )
        for r in rows
    ]


@router.post("/audit", response_model=AuthAuditLogResponse)
async def record_audit_event(
    audit: AuthAuditLog,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> AuthAuditLogResponse:
    row = AuditLogModel(
        organization_id=payload.org_id,
        user_id=audit.user_id or payload.sub,
        action=audit.action,
        resource=audit.resource,
        success=audit.success,
        ip_address=audit.ip_address,
        user_agent=audit.user_agent,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    logger.info(
        "Audit persisted: user=%s action=%s resource=%s success=%s",
        row.user_id,
        row.action,
        row.resource,
        row.success,
    )
    return AuthAuditLogResponse(
        user_id=row.user_id,
        org_id=str(row.organization_id),
        action=row.action,
        resource=row.resource,
        success=row.success,
        ip_address=row.ip_address,
        user_agent=row.user_agent,
        timestamp=row.created_at.isoformat(),
    )
