from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres import TargetAgent
from app.domain.evaluations import TargetAgentEntity


class SQLAgentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _map_agent_to_entity(self, agent: TargetAgent) -> TargetAgentEntity:
        return TargetAgentEntity(
            id=agent.id,
            organization_id=agent.organization_id,
            name=agent.name,
            description=agent.description,
            agent_type=agent.agent_type.value if hasattr(agent.agent_type, "value") else str(agent.agent_type),
            endpoint_url=agent.endpoint_url,
            model_name=agent.model_name,
            system_prompt=agent.system_prompt,
            api_key_encrypted=agent.api_key_encrypted,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )

    async def get_agent(self, agent_id: uuid.UUID, organization_id: uuid.UUID) -> TargetAgentEntity | None:
        result = await self.db.execute(
            select(TargetAgent).where(
                TargetAgent.id == agent_id,
                TargetAgent.organization_id == organization_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._map_agent_to_entity(row) if row else None

    async def list_agents(self, organization_id: uuid.UUID) -> list[TargetAgentEntity]:
        result = await self.db.execute(
            select(TargetAgent).where(TargetAgent.organization_id == organization_id)
        )
        rows = result.scalars().all()
        return [self._map_agent_to_entity(r) for r in rows]
