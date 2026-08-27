from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import TokenPayload, require_member, require_admin, verify_token
from app.models.postgres import TargetAgent as TargetAgentModel
from app.schemas.agents import TargetAgentCreate, TargetAgentList, TargetAgentResponse, TargetAgentUpdate

logger = logging.getLogger("snt_ai.routers.agents")

router = APIRouter(prefix="/agents", tags=["Target Agents"])


@router.post("", response_model=TargetAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: TargetAgentCreate,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> TargetAgentModel:
    agent = TargetAgentModel(
        organization_id=payload.org_id,
        name=body.name,
        description=body.description,
        agent_type=body.agent_type,
        endpoint_url=body.endpoint_url,
        system_prompt=body.system_prompt,
        model_name=body.model_name,
        config=body.config or {},
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    logger.info("Agent created: %s (org=%s)", agent.id, payload.org_id)
    return agent


@router.get("", response_model=TargetAgentList)
async def list_agents(
    page: int = 1,
    per_page: int = 20,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> TargetAgentList:
    offset = (page - 1) * per_page
    count_q = select(func.count(TargetAgentModel.id)).where(
        TargetAgentModel.organization_id == payload.org_id
    )
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(TargetAgentModel)
        .where(TargetAgentModel.organization_id == payload.org_id)
        .offset(offset)
        .limit(per_page)
        .order_by(TargetAgentModel.created_at.desc())
    )
    result = await db.execute(q)
    agents = result.scalars().all()

    return TargetAgentList(
        items=[TargetAgentResponse.model_validate(a) for a in agents],
        total=total,
    )


@router.get("/{agent_id}", response_model=TargetAgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> TargetAgentModel:
    result = await db.execute(
        select(TargetAgentModel).where(
            TargetAgentModel.id == agent_id,
            TargetAgentModel.organization_id == payload.org_id,
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=TargetAgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    body: TargetAgentUpdate,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> TargetAgentModel:
    result = await db.execute(
        select(TargetAgentModel).where(
            TargetAgentModel.id == agent_id,
            TargetAgentModel.organization_id == payload.org_id,
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.flush()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID,
    payload: TokenPayload = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    result = await db.execute(
        select(TargetAgentModel).where(
            TargetAgentModel.id == agent_id,
            TargetAgentModel.organization_id == payload.org_id,
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    await db.delete(agent)
    await db.flush()
