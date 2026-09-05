from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import TokenPayload, require_member, require_admin, verify_token
from app.models.postgres import EvaluationSuite as EvaluationSuiteModel
from app.schemas.suites import (
    EvaluationSuiteCreate,
    EvaluationSuiteList,
    EvaluationSuiteResponse,
    EvaluationSuiteUpdate,
)

logger = logging.getLogger("snt_ai.routers.suites")

router = APIRouter(prefix="/suites", tags=["Evaluation Suites"])


@router.post("", response_model=EvaluationSuiteResponse, status_code=status.HTTP_201_CREATED)
async def create_suite(
    body: EvaluationSuiteCreate,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> EvaluationSuiteResponse:
    suite = EvaluationSuiteModel(
        organization_id=payload.org_id,
        name=body.name,
        description=body.description,
        persona_config=body.persona_config or [],
        chaos_profiles=body.chaos_profiles or {},
        judge_config=body.judge_config or {},
    )
    db.add(suite)
    await db.flush()
    await db.refresh(suite)
    logger.info("Suite created: %s (org=%s)", suite.id, payload.org_id)
    try:
        return EvaluationSuiteResponse.model_validate(suite)
    except Exception:
        logger.exception("Failed to serialize suite %s", suite.id)
        raise


@router.get("", response_model=EvaluationSuiteList)
async def list_suites(
    page: int = 1,
    per_page: int = 20,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> EvaluationSuiteList:
    offset = (page - 1) * per_page
    count_q = select(func.count(EvaluationSuiteModel.id)).where(
        EvaluationSuiteModel.organization_id == payload.org_id
    )
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(EvaluationSuiteModel)
        .where(EvaluationSuiteModel.organization_id == payload.org_id)
        .offset(offset)
        .limit(per_page)
        .order_by(EvaluationSuiteModel.created_at.desc())
    )
    result = await db.execute(q)
    suites = result.scalars().all()

    return EvaluationSuiteList(
        items=[EvaluationSuiteResponse.model_validate(s) for s in suites],
        total=total,
    )


@router.get("/{suite_id}", response_model=EvaluationSuiteResponse)
async def get_suite(
    suite_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> EvaluationSuiteModel:
    org_id = uuid.UUID(str(payload.org_id))
    result = await db.execute(
        select(EvaluationSuiteModel).where(
            EvaluationSuiteModel.id == suite_id,
            EvaluationSuiteModel.organization_id == org_id,
        )
    )
    suite = result.scalar_one_or_none()
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
    return suite


@router.patch("/{suite_id}", response_model=EvaluationSuiteResponse)
async def update_suite(
    suite_id: uuid.UUID,
    body: EvaluationSuiteUpdate,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> EvaluationSuiteModel:
    result = await db.execute(
        select(EvaluationSuiteModel).where(
            EvaluationSuiteModel.id == suite_id,
            EvaluationSuiteModel.organization_id == payload.org_id,
        )
    )
    suite = result.scalar_one_or_none()
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(suite, field, value)

    await db.flush()
    await db.refresh(suite)
    return suite


@router.delete("/{suite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_suite(
    suite_id: uuid.UUID,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    result = await db.execute(
        select(EvaluationSuiteModel).where(
            EvaluationSuiteModel.id == suite_id,
            EvaluationSuiteModel.organization_id == payload.org_id,
        )
    )
    suite = result.scalar_one_or_none()
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
    await db.delete(suite)
    await db.flush()
