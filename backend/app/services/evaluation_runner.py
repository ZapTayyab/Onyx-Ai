from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from app.core.database import _get_session_factory
from app.repositories.evaluations import SQLEvaluationRepository
from app.services.run_evaluation_use_case import RunEvaluationUseCase

logger = logging.getLogger("snt_ai.services.evaluation_runner")


class EvaluationRunner:
    def __init__(self, temporal_client: Any | None = None) -> None:
        self._temporal = temporal_client

    async def _run_locally_in_bg(
        self,
        organization_id: str,
        suite_id: str,
        agent_id: str,
        run_id: uuid.UUID,
    ) -> None:
        factory = _get_session_factory()
        async with factory() as db:
            repo = SQLEvaluationRepository(db)
            use_case = RunEvaluationUseCase(eval_repo=repo)
            try:
                await use_case.execute(
                    organization_id=uuid.UUID(organization_id),
                    suite_id=uuid.UUID(suite_id),
                    agent_id=uuid.UUID(agent_id),
                    run_id=run_id,
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("Background evaluation run %s failed", run_id)

    async def run_locally(
        self,
        organization_id: str,
        suite_id: str,
        agent_id: str,
        run_id: uuid.UUID,
        db: Any,
    ) -> dict[str, Any]:
        repo = SQLEvaluationRepository(db)
        use_case = RunEvaluationUseCase(eval_repo=repo)
        return await use_case.execute(
            organization_id=uuid.UUID(organization_id),
            suite_id=uuid.UUID(suite_id),
            agent_id=uuid.UUID(agent_id),
            run_id=run_id,
        )

    async def run_via_temporal(
        self,
        organization_id: str,
        suite_id: str,
        agent_id: str,
        run_id: uuid.UUID,
        db: Any,
    ) -> None:
        if self._temporal is None:
            logger.warning("Temporal client not configured; falling back to local execution")
            asyncio.create_task(self._run_locally_in_bg(
                organization_id, suite_id, agent_id, run_id,
            ))
            return

        from app.workflows.evaluation_workflow import EvaluationWorkflow

        repo = SQLEvaluationRepository(db)
        org_uuid = uuid.UUID(organization_id)
        suite = await repo.get_suite(uuid.UUID(suite_id), org_uuid)
        agent = await repo.get_agent(uuid.UUID(agent_id), org_uuid)
        run = await repo.get_run(run_id, org_uuid)

        handle = await self._temporal.start_workflow(
            EvaluationWorkflow.run,
            args=[{
                "run_id": str(run_id),
                "organization_id": organization_id,
                "suite_config": {
                    "persona_config": suite.persona_config if suite else [],
                    "chaos_profiles": suite.chaos_profiles if suite else {},
                    "judge_config": suite.judge_config if suite else {},
                },
                "agent_config": {
                    "system_prompt": agent.system_prompt if agent else "",
                    "model_name": agent.model_name if agent else "unknown",
                    "agent_type": agent.agent_type if agent else "mock",
                    "endpoint_url": agent.endpoint_url if agent else None,
                    "api_key": agent.api_key_encrypted if agent else None,
                },
            }],
            id=f"eval-run-{run_id}",
            task_queue="snt-ai-evaluation-queue",
        )

        if run:
            from app.domain.evaluations import RunStatus
            run.status = RunStatus.RUNNING
            await repo.update_run(run)

        logger.info("Temporal workflow submitted: run=%s workflow_id=eval-run-%s", run_id, run_id)

        async def _await_result():
            try:
                result = await handle.result()
                factory = _get_session_factory()
                async with factory() as bg_db:
                    bg_repo = SQLEvaluationRepository(bg_db)
                    bg_run = await bg_repo.get_run(run_id, org_uuid)
                    if bg_run is not None:
                        from app.domain.evaluations import RunStatus
                        bg_run.status = RunStatus.COMPLETED
                        bg_run.aggregate_score = result.get("aggregate_score")
                        bg_run.total_sessions = result.get("total_sessions", 0)
                        bg_run.completed_sessions = result.get("total_sessions", 0)
                        await bg_repo.update_run(bg_run)
                        await bg_db.commit()
            except Exception as exc:
                logger.error("Temporal workflow failed: run=%s error=%s", run_id, exc)
                factory = _get_session_factory()
                async with factory() as bg_db:
                    bg_repo = SQLEvaluationRepository(bg_db)
                    bg_run = await bg_repo.get_run(run_id, org_uuid)
                    if bg_run is not None:
                        from app.domain.evaluations import RunStatus
                        bg_run.status = RunStatus.FAILED
                        bg_run.error_message = str(exc)
                        await bg_repo.update_run(bg_run)
                        await bg_db.commit()

        asyncio.create_task(_await_result())
