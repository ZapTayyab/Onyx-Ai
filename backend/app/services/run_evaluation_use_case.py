from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
import uuid

from app.domain.evaluations import (
    EvaluationSuiteEntity,
    RunMetadataEntity,
    RunStatus,
    TargetAgentEntity,
)
from app.repositories.evaluations import (
    ClickHouseTraceRepository,
    IEvaluationRepository,
)
from app.services.chaos_injector import (
    ChaosInjector,
    ChaosProfile,
    MockAgentProvider,
    RemoteAgentProvider,
)
from app.services.clickhouse_flusher import ClickHouseFlusher
from app.services.llm_judge import LLMJudge, SessionVerdict
from app.services.persona_generator import PersonaGenerator, PersonaProfile

logger = logging.getLogger("snt_ai.use_cases.run_evaluation")


class RunEvaluationUseCase:
    """Use-case orchestrating persona generation -> chaos injection -> agent response -> LLM judge -> clickhouse trace logging."""

    def __init__(
        self,
        eval_repo: IEvaluationRepository,
        trace_repo: ClickHouseTraceRepository | None = None,
        judge: LLMJudge | None = None,
        flusher: ClickHouseFlusher | None = None,
    ) -> None:
        self.eval_repo = eval_repo
        self.trace_repo = trace_repo or ClickHouseTraceRepository()
        self.judge = judge or LLMJudge()
        self.flusher = flusher or ClickHouseFlusher()
        self.generator = PersonaGenerator()

    async def execute(
        self,
        organization_id: uuid.UUID,
        suite_id: uuid.UUID,
        agent_id: uuid.UUID,
        run_id: uuid.UUID,
    ) -> dict[str, Any]:
        suite = await self.eval_repo.get_suite(suite_id, organization_id)
        if suite is None:
            raise ValueError(f"Suite {suite_id} not found")

        agent = await self.eval_repo.get_agent(agent_id, organization_id)
        if agent is None:
            raise ValueError(f"Agent {agent_id} not found")

        run = await self.eval_repo.get_run(run_id, organization_id)
        if run is None:
            raise ValueError(f"Run {run_id} not found")

        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        await self.eval_repo.update_run(run)

        persona_configs = suite.persona_config
        chaos_config = suite.chaos_profiles
        system_prompt = agent.system_prompt or ""
        model_name = agent.model_name or "unknown"

        profiles: list[PersonaProfile] = []
        for pc in persona_configs:
            if isinstance(pc, dict):
                profiles.append(PersonaProfile(**pc))

        if not profiles:
            profiles = self.generator.get_builtin_profiles()

        session_verdicts: list[SessionVerdict] = []
        chaos_profile = ChaosProfile.from_dict(chaos_config) if chaos_config else ChaosProfile()

        if agent.endpoint_url:
            agent_provider = RemoteAgentProvider(
                endpoint_url=agent.endpoint_url,
                api_key=agent.api_key_encrypted,
                model_name=agent.model_name,
                system_prompt=system_prompt,
            )
        else:
            agent_provider = MockAgentProvider(system_prompt)

        try:
            for profile in profiles:
                logger.debug("Evaluating persona: %s", profile.name)

                script = self.generator.generate_conversation_script(profile, max_turns=10)
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

                session_verdict = self.judge.evaluate_session(
                    session_id=f"{run.id}-{profile.name.lower().replace(' ', '-')}",
                    persona_name=profile.name,
                    turns=turns_data,
                    context=system_prompt,
                )
                session_verdicts.append(session_verdict)

                await self.flusher.flush_turn_traces(
                    organization_id=str(organization_id),
                    run_id=str(run.id),
                    session_id=session_verdict.session_id,
                    persona_name=profile.name,
                    turns=turns_data,
                    turn_verdicts=session_verdict.turn_verdicts,
                    chaos_log=chaos_log,
                    model_name=model_name,
                )

            total_sessions = len(session_verdicts)
            avg_score = round(sum(sv.aggregate_score for sv in session_verdicts) / total_sessions, 2) if total_sessions > 0 else 0.0

            run.status = RunStatus.COMPLETED
            run.aggregate_score = avg_score
            run.total_sessions = total_sessions
            run.completed_sessions = total_sessions
            run.completed_at = datetime.now(timezone.utc)
            run.summary_metrics = {
                "sessions": [
                    {
                        "session_id": sv.session_id,
                        "persona_name": sv.persona_name,
                        "aggregate_score": sv.aggregate_score,
                        "passed_turns": sv.passed_turns,
                        "total_turns": sv.total_turns,
                    }
                    for sv in session_verdicts
                ]
            }

        except Exception as exc:
            logger.error("Evaluation run %s failed: %s", run.id, exc)
            run.status = RunStatus.FAILED
            run.error_message = str(exc)

        await self.eval_repo.update_run(run)

        return {
            "run_id": str(run.id),
            "status": run.status.value,
            "aggregate_score": run.aggregate_score,
            "total_sessions": run.total_sessions,
            "completed_sessions": run.completed_sessions,
        }
