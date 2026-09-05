from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Protocol, Sequence
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clickhouse import clickhouse_mgr
from app.models.clickhouse.traces import (
    INSERT_TURN_TRACE,
    QUERY_AGGREGATE_METRICS_BY_RUN,
    QUERY_REGRESSION_DELTA,
    QUERY_TRACES_BY_RUN,
)
from app.models.postgres import EvaluationSuite, RunMetadata, TargetAgent
from app.domain.evaluations import (
    EvaluationSuiteEntity,
    RunMetadataEntity,
    RunStatus,
    TargetAgentEntity,
    TurnTraceEntity,
)


class IEvaluationRepository(Protocol):
    async def get_suite(self, suite_id: uuid.UUID, organization_id: uuid.UUID) -> EvaluationSuiteEntity | None: ...
    async def get_agent(self, agent_id: uuid.UUID, organization_id: uuid.UUID) -> TargetAgentEntity | None: ...
    async def create_run(
        self,
        organization_id: uuid.UUID,
        suite_id: uuid.UUID,
        agent_id: uuid.UUID,
        triggered_by: uuid.UUID | None,
        total_sessions: int,
    ) -> RunMetadataEntity: ...
    async def get_run(self, run_id: uuid.UUID, organization_id: uuid.UUID) -> RunMetadataEntity | None: ...
    async def list_runs(
        self, organization_id: uuid.UUID, page: int = 1, per_page: int = 20
    ) -> Sequence[RunMetadataEntity]: ...
    async def update_run(self, run_entity: RunMetadataEntity) -> RunMetadataEntity: ...


class SQLEvaluationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _map_suite_to_entity(self, suite: EvaluationSuite) -> EvaluationSuiteEntity:
        return EvaluationSuiteEntity(
            id=suite.id,
            organization_id=suite.organization_id,
            name=suite.name,
            description=suite.description,
            persona_config=suite.persona_config or [],
            chaos_profiles=suite.chaos_profiles or {},
            judge_config=suite.judge_config or {},
            is_active=suite.is_active,
            created_at=suite.created_at,
            updated_at=suite.updated_at,
        )

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

    def _map_run_to_entity(self, run: RunMetadata) -> RunMetadataEntity:
        return RunMetadataEntity(
            id=run.id,
            organization_id=run.organization_id,
            suite_id=run.suite_id,
            agent_id=run.agent_id,
            status=RunStatus(run.status.value) if hasattr(run.status, "value") else RunStatus(run.status),
            aggregate_score=run.aggregate_score,
            total_sessions=run.total_sessions,
            completed_sessions=run.completed_sessions,
            summary_metrics=run.summary_metrics or {},
            error_message=run.error_message,
            started_at=run.started_at,
            completed_at=run.completed_at,
            triggered_by=run.triggered_by,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )

    async def get_suite(self, suite_id: uuid.UUID, organization_id: uuid.UUID) -> EvaluationSuiteEntity | None:
        result = await self.db.execute(
            select(EvaluationSuite).where(
                EvaluationSuite.id == suite_id,
                EvaluationSuite.organization_id == organization_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._map_suite_to_entity(row) if row else None

    async def get_agent(self, agent_id: uuid.UUID, organization_id: uuid.UUID) -> TargetAgentEntity | None:
        result = await self.db.execute(
            select(TargetAgent).where(
                TargetAgent.id == agent_id,
                TargetAgent.organization_id == organization_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._map_agent_to_entity(row) if row else None

    async def create_run(
        self,
        organization_id: uuid.UUID,
        suite_id: uuid.UUID,
        agent_id: uuid.UUID,
        triggered_by: uuid.UUID | None,
        total_sessions: int,
    ) -> RunMetadataEntity:
        from app.config import RunStatus as ConfigRunStatus
        run_model = RunMetadata(
            organization_id=organization_id,
            suite_id=suite_id,
            agent_id=agent_id,
            status=ConfigRunStatus.PENDING,
            triggered_by=triggered_by,
            total_sessions=total_sessions,
        )
        self.db.add(run_model)
        await self.db.flush()
        await self.db.refresh(run_model)
        return self._map_run_to_entity(run_model)

    async def get_run(self, run_id: uuid.UUID, organization_id: uuid.UUID) -> RunMetadataEntity | None:
        result = await self.db.execute(
            select(RunMetadata).where(
                RunMetadata.id == run_id,
                RunMetadata.organization_id == organization_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._map_run_to_entity(row) if row else None

    async def list_runs(
        self, organization_id: uuid.UUID, page: int = 1, per_page: int = 20
    ) -> Sequence[RunMetadataEntity]:
        offset = (page - 1) * per_page
        q = (
            select(RunMetadata)
            .where(RunMetadata.organization_id == organization_id)
            .offset(offset)
            .limit(per_page)
            .order_by(RunMetadata.created_at.desc())
        )
        result = await self.db.execute(q)
        rows = result.scalars().all()
        return [self._map_run_to_entity(r) for r in rows]

    async def update_run(self, run_entity: RunMetadataEntity) -> RunMetadataEntity:
        row = await self.db.get(RunMetadata, run_entity.id)
        if row is None:
            raise ValueError(f"RunMetadata {run_entity.id} not found")
        from app.config import RunStatus as ConfigRunStatus
        row.status = ConfigRunStatus(run_entity.status.value)
        row.aggregate_score = run_entity.aggregate_score
        row.total_sessions = run_entity.total_sessions
        row.completed_sessions = run_entity.completed_sessions
        row.summary_metrics = run_entity.summary_metrics
        row.error_message = run_entity.error_message
        row.started_at = run_entity.started_at
        row.completed_at = run_entity.completed_at
        await self.db.flush()
        return self._map_run_to_entity(row)


class ClickHouseTraceRepository:
    async def get_traces_by_run(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> list[TurnTraceEntity]:
        rows = await clickhouse_mgr.execute(
            QUERY_TRACES_BY_RUN,
            {"organization_id": str(organization_id), "run_id": str(run_id)},
        )
        turns: list[TurnTraceEntity] = []
        for row in rows:
            turns.append(
                TurnTraceEntity(
                    organization_id=organization_id,
                    session_id=row[0],
                    run_id=run_id,
                    turn_id=row[1],
                    timestamp=row[2] if isinstance(row[2], datetime) else datetime.fromisoformat(str(row[2])),
                    speaker=row[3],
                    turn_text=row[4],
                    token_count=row[5],
                    latency_ms=row[6],
                    model_name=row[7],
                    chaos_injected=json.loads(row[8]) if row[8] else {},
                    scores=json.loads(row[9]) if row[9] else {},
                    metadata=json.loads(row[10]) if row[10] else {},
                )
            )
        return turns

    async def get_aggregate_metrics(
        self, organization_id: uuid.UUID, run_id: uuid.UUID
    ) -> dict[str, Any] | None:
        rows = await clickhouse_mgr.execute(
            QUERY_AGGREGATE_METRICS_BY_RUN,
            {"organization_id": str(organization_id), "run_id": str(run_id)},
        )
        if not rows:
            return None
        row = rows[0]
        return {
            "run_id": run_id,
            "total_turns": row[1],
            "avg_latency_ms": row[2],
            "p50_latency_ms": row[3],
            "p90_latency_ms": row[4],
            "p99_latency_ms": row[5],
            "total_tokens": row[6],
            "avg_tokens_per_turn": row[7],
            "total_sessions": row[8],
        }

    async def get_regression_delta(
        self, current_run_id: uuid.UUID, baseline_run_id: uuid.UUID
    ) -> dict[str, float] | None:
        rows = await clickhouse_mgr.execute(
            QUERY_REGRESSION_DELTA,
            {
                "current_run_id": str(current_run_id),
                "baseline_run_id": str(baseline_run_id),
            },
        )
        if not rows:
            return None
        row = rows[0]
        return {
            "groundedness_delta": row[0] or 0.0,
            "compliance_delta": row[1] or 0.0,
            "robustness_delta": row[2] or 0.0,
            "p90_latency_delta": row[3] or 0.0,
        }
