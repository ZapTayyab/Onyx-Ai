from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import RunStatus
from app.core.database import _get_session_factory
from app.models.postgres import EvaluationSuite, RunMetadata, TargetAgent

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
        """Run evaluation in a background task with its own DB session."""
        factory = _get_session_factory()
        async with factory() as db:
            run = await db.get(RunMetadata, run_id)
            if run is None:
                logger.error("Run %s not found for background execution", run_id)
                return
            try:
                await self.run_locally(organization_id, suite_id, agent_id, run, db)
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("Background evaluation run %s failed", run_id)

    async def run_locally(
        self,
        organization_id: str,
        suite_id: str,
        agent_id: str,
        run: RunMetadata,
        db: AsyncSession,
    ) -> dict[str, Any]:
        from app.services.chaos_injector import ChaosInjector, ChaosProfile, MockAgentProvider, RemoteAgentProvider
        from app.services.clickhouse_flusher import ClickHouseFlusher
        from app.services.llm_judge import LLMJudge, SessionVerdict
        from app.services.persona_generator import PersonaCategory, PersonaGenerator, PersonaProfile

        logger.info("Starting local evaluation run=%s", run.id)

        suite_result = await db.execute(
            select(EvaluationSuite).where(EvaluationSuite.id == suite_id)
        )
        suite = suite_result.scalar_one_or_none()
        if suite is None:
            raise ValueError(f"Suite {suite_id} not found")

        agent_result = await db.execute(
            select(TargetAgent).where(TargetAgent.id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        if agent is None:
            raise ValueError(f"Agent {agent_id} not found")

        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        await db.flush()

        persona_configs = suite.persona_config or []
        chaos_config = suite.chaos_profiles or {}
        judge_config = suite.judge_config or {}
        system_prompt = agent.system_prompt or ""
        model_name = agent.model_name or "unknown"

        generator = PersonaGenerator()
        profiles: list[PersonaProfile] = []
        for pc in persona_configs:
            profiles.append(PersonaProfile(**pc))

        if not profiles:
            profiles = generator.get_builtin_profiles()

        session_verdicts: list[SessionVerdict] = []
        chaos_profile = ChaosProfile.from_dict(chaos_config) if chaos_config else ChaosProfile()
        judge = LLMJudge()
        flusher = ClickHouseFlusher()

        if agent.endpoint_url:
            agent_provider = RemoteAgentProvider(
                endpoint_url=agent.endpoint_url,
                api_key=agent.api_key_encrypted,
                model_name=agent.model_name,
                system_prompt=system_prompt,
            )
            logger.info("Using remote agent provider: %s", agent.endpoint_url)
        else:
            agent_provider = MockAgentProvider(system_prompt)
            logger.debug("Using mock agent provider (no endpoint configured)")

        try:
            for profile in profiles:
                logger.debug("Evaluating persona: %s", profile.name)

                script = generator.generate_conversation_script(profile, max_turns=10)
                chaos = ChaosInjector(chaos_profile)
                turns_data: list[dict[str, Any]] = []
                chaos_log: list[dict[str, Any]] = []

                for turn_idx, user_msg in enumerate(script):
                    user_msg_prepped, pre_effects = await chaos.apply_pre_turn(turn_idx, user_msg)
                    response_text, latency_ms, token_count = await agent_provider.generate_response(
                        user_msg_prepped, turns_data
                    )
                    latency_ms, post_effects = await chaos.apply_post_turn(turn_idx, latency_ms)
                    response_text, guardrail_effects = await chaos.apply_guardrail_check(turn_idx, response_text)

                    turn_effects = {**pre_effects, **post_effects, **guardrail_effects}
                    chaos_log.append(turn_effects)

                    turns_data.append({
                        "user": user_msg_prepped,
                        "agent": response_text,
                        "latency_ms": latency_ms,
                        "token_count_user": len(user_msg_prepped.split()),
                        "token_count_agent": token_count,
                        "timestamp": datetime.now(timezone.utc),
                    })

                session_verdict = judge.evaluate_session(
                    session_id=f"{run.id}-{profile.name.lower().replace(' ', '-')}",
                    persona_name=profile.name,
                    turns=turns_data,
                    context=system_prompt,
                )
                session_verdicts.append(session_verdict)

                await flusher.flush_turn_traces(
                    organization_id=organization_id,
                    run_id=str(run.id),
                    session_id=session_verdict.session_id,
                    persona_name=profile.name,
                    turns=turns_data,
                    turn_verdicts=session_verdict.turn_verdicts,
                    chaos_log=chaos_log,
                    model_name=model_name,
                )

            await flusher.update_run_metadata(db, run, session_verdicts)
            run.status = RunStatus.COMPLETED

        except Exception as exc:
            logger.error("Evaluation run %s failed: %s", run.id, exc)
            run.status = RunStatus.FAILED
            run.error_message = str(exc)

        await db.flush()
        logger.info("Local evaluation complete: run=%s score=%s", run.id, run.aggregate_score)

        return {
            "run_id": str(run.id),
            "status": run.status.value,
            "aggregate_score": run.aggregate_score,
            "total_sessions": run.total_sessions,
            "completed_sessions": run.completed_sessions,
        }

    async def run_via_temporal(
        self,
        organization_id: str,
        suite_id: str,
        agent_id: str,
        run: RunMetadata,
        db: AsyncSession,
    ) -> None:
        """Submit evaluation to Temporal. Falls back to local if Temporal is unavailable.

        Does NOT await workflow completion — the Temporal Worker executes the
        workflow and writes results to ClickHouse. A background callback updates
        the run status when the workflow finishes.
        """
        if self._temporal is None:
            logger.warning("Temporal client not configured; falling back to local execution")
            asyncio.create_task(self._run_locally_in_bg(
                organization_id, suite_id, agent_id, run.id,
            ))
            return

        from app.workflows.evaluation_workflow import EvaluationWorkflow

        suite_result = await db.execute(
            select(EvaluationSuite).where(EvaluationSuite.id == suite_id)
        )
        suite = suite_result.scalar_one_or_none()
        agent_result = await db.execute(
            select(TargetAgent).where(TargetAgent.id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()

        handle = await self._temporal.start_workflow(
            EvaluationWorkflow.run,
            args=[{
                "run_id": str(run.id),
                "organization_id": organization_id,
                "suite_config": {
                    "persona_config": suite.persona_config if suite else [],
                    "chaos_profiles": suite.chaos_profiles if suite else {},
                    "judge_config": suite.judge_config if suite else {},
                },
                "agent_config": {
                    "system_prompt": agent.system_prompt if agent else "",
                    "model_name": agent.model_name if agent else "unknown",
                    "agent_type": agent.agent_type.value if agent else "mock",
                    "endpoint_url": agent.endpoint_url if agent else None,
                    "api_key": agent.api_key_encrypted if agent else None,
                },
            }],
            id=f"eval-run-{run.id}",
            task_queue="snt-ai-evaluation-queue",
        )

        run.status = RunStatus.RUNNING
        await db.flush()

        logger.info(
            "Temporal workflow submitted: run=%s workflow_id=eval-run-%s",
            run.id,
            run.id,
        )

        async def _await_result():
            try:
                result = await handle.result()
                factory = _get_session_factory()
                async with factory() as bg_db:
                    bg_run = await bg_db.get(RunMetadata, run.id)
                    if bg_run is not None:
                        bg_run.status = RunStatus.COMPLETED
                        bg_run.aggregate_score = result.get("aggregate_score")
                        bg_run.total_sessions = result.get("total_sessions", 0)
                        bg_run.completed_sessions = result.get("total_sessions", 0)
                        await bg_db.commit()
                        logger.info(
                            "Temporal workflow completed: run=%s score=%s",
                            run.id, bg_run.aggregate_score,
                        )
            except Exception as exc:
                logger.error("Temporal workflow failed: run=%s error=%s", run.id, exc)
                factory = _get_session_factory()
                async with factory() as bg_db:
                    bg_run = await bg_db.get(RunMetadata, run.id)
                    if bg_run is not None:
                        bg_run.status = RunStatus.FAILED
                        bg_run.error_message = str(exc)
                        await bg_db.commit()

        asyncio.create_task(_await_result())
