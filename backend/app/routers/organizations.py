from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import BillingPlan, RunStatus, get_config
from app.core.database import get_async_session
from app.core.security import TokenPayload, require_admin, require_member
from app.models.postgres import Organization as OrganizationModel
from app.models.postgres import RunMetadata as RunMetadataModel
from app.models.postgres import User as UserModel
from app.schemas.organizations import (
    BillingPlanUpdate,
    InviteUserRequest,
    InviteUserResponse,
    MemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
    RunHistoryResponse,
    SSOConfigRequest,
    SSOConfigResponse,
    UsageResponse,
)

logger = logging.getLogger("snt_ai.routers.organizations")

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> OrganizationModel:
    result = await db.execute(
        select(OrganizationModel).where(OrganizationModel.id == payload.org_id)
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.patch("/me", response_model=OrganizationResponse)
async def update_organization(
    body: OrganizationUpdate,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> OrganizationModel:
    result = await db.execute(
        select(OrganizationModel).where(OrganizationModel.id == payload.org_id)
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    if body.name is not None:
        org.name = body.name
    if body.settings is not None:
        org.settings = body.settings
    await db.flush()
    await db.refresh(org)
    return org


@router.get("/me/members", response_model=list[MemberResponse])
async def list_members(
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> list[UserModel]:
    result = await db.execute(
        select(UserModel).where(
            UserModel.organization_id == payload.org_id,
            UserModel.is_active == True,
        ).order_by(UserModel.created_at)
    )
    return list(result.scalars().all())


@router.post("/me/invite", response_model=InviteUserResponse)
async def invite_user(
    body: InviteUserRequest,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> InviteUserResponse:
    existing = await db.execute(
        select(UserModel).where(
            UserModel.email == body.email,
            UserModel.organization_id == payload.org_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already in organization")

    user = UserModel(
        organization_id=payload.org_id,
        email=body.email,
        role=body.role,
        auth_provider_id=f"pending:{uuid.uuid4()}",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    logger.info("User invited: %s to org %s (role=%s)", body.email, payload.org_id, body.role)
    return InviteUserResponse(id=user.id, email=user.email, role=user.role, status="invited")


@router.delete("/me/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: uuid.UUID,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    result = await db.execute(
        select(UserModel).where(
            UserModel.id == user_id,
            UserModel.organization_id == payload.org_id,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    await db.flush()


@router.get("/me/usage", response_model=UsageResponse)
async def get_usage(
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> UsageResponse:
    org_id = payload.org_id
    runs_result = await db.execute(
        select(RunMetadataModel).where(RunMetadataModel.organization_id == org_id)
    )
    runs = runs_result.scalars().all()
    total_runs = len(runs)
    completed_runs = sum(1 for r in runs if r.status == RunStatus.COMPLETED)
    failed_runs = sum(1 for r in runs if r.status == RunStatus.FAILED)
    total_sessions = sum(r.total_sessions for r in runs)

    members_result = await db.execute(
        select(UserModel).where(
            UserModel.organization_id == org_id,
            UserModel.is_active == True,
        )
    )
    member_count = len(members_result.scalars().all())

    return UsageResponse(
        total_runs=total_runs,
        completed_runs=completed_runs,
        failed_runs=failed_runs,
        total_sessions=total_sessions,
        active_members=member_count,
    )


@router.get("/me/billing", response_model=BillingPlan)
async def get_billing_plan(
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> BillingPlan:
    result = await db.execute(
        select(OrganizationModel.billing_plan).where(OrganizationModel.id == payload.org_id)
    )
    plan = result.scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return plan


@router.patch("/me/billing", response_model=BillingPlan)
async def update_billing_plan(
    body: BillingPlanUpdate,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> BillingPlan:
    result = await db.execute(
        select(OrganizationModel).where(OrganizationModel.id == payload.org_id)
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    org.billing_plan = body.plan
    await db.flush()
    await db.refresh(org)
    logger.info("Billing plan updated for org %s: %s", payload.org_id, body.plan)
    return org.billing_plan


@router.get("/me/sso", response_model=SSOConfigResponse)
async def get_sso_config(
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> SSOConfigResponse:
    result = await db.execute(
        select(OrganizationModel).where(OrganizationModel.id == payload.org_id)
    )
    org = result.scalar_one_or_none()
    if org is None or not org.settings:
        return SSOConfigResponse(enabled=False, provider=None)
    settings = org.settings
    if isinstance(settings, str):
        import json
        settings = json.loads(settings)
    return SSOConfigResponse(
        enabled=settings.get("sso_enabled", False),
        provider=settings.get("sso_provider"),
        domain=settings.get("sso_domain"),
        metadata_url=settings.get("sso_metadata_url"),
    )


@router.put("/me/sso", response_model=SSOConfigResponse)
async def configure_sso(
    body: SSOConfigRequest,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> SSOConfigResponse:
    result = await db.execute(
        select(OrganizationModel).where(OrganizationModel.id == payload.org_id)
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    current = {}
    if org.settings:
        if isinstance(org.settings, str):
            import json
            current = json.loads(org.settings)
        else:
            current = org.settings

    current.update({
        "sso_enabled": body.enabled,
        "sso_provider": body.provider,
        "sso_domain": body.domain,
        "sso_metadata_url": body.metadata_url,
    })
    import json
    org.settings = json.dumps(current)
    await db.flush()
    logger.info("SSO configured for org %s: provider=%s enabled=%s", payload.org_id, body.provider, body.enabled)

    return SSOConfigResponse(
        enabled=body.enabled,
        provider=body.provider,
        domain=body.domain,
        metadata_url=body.metadata_url,
    )
