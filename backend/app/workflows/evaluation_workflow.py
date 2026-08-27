from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

# Logger must be defined before the try/except so ImportError handler can use it
logger = logging.getLogger("snt_ai.workflows.evaluation")

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy

    workflow_defn = workflow.defn
    workflow_run = workflow.run
    _temporal_available = True
except ImportError:
    logger.warning(
        "temporalio not installed — EvaluationWorkflow will NOT be registered "
        "with Temporal server. Install 'temporalio' for distributed workflow execution."
    )
    workflow_defn = lambda cls: cls  # noqa: E731
    workflow_run = lambda fn: fn      # noqa: E731
    _temporal_available = False

from app.config import RunStatus, get_config
from app.services.chaos_injector import ChaosInjector, ChaosProfile, MockAgentProvider, RemoteAgentProvider
from app.services.clickhouse_flusher import ClickHouseFlusher
from app.services.llm_judge import LLMJudge, SessionVerdict
from app.services.persona_generator import PersonaCategory, PersonaGenerator, PersonaProfile


TASK_QUEUE = "snt-ai-evaluation-queue"
MAX_TURNS_PER_SESSION = 10
DEFAULT_TIMEOUT = timedelta(minutes=30)


@workflow_defn
class EvaluationWorkflow:
    @workflow_run
    async def run(self, params: dict[str, Any]) -> dict[str, Any]:
        if not _temporal_available:
            raise RuntimeError(
                "temporalio package is required to execute EvaluationWorkflow. "
                "Install it with: pip install temporalio"
            )
        logger.info("Starting EvaluationWorkflow with params: %s", params)

        run_id = params["run_id"]
        organization_id = params["organization_id"]
        suite_config = params.get("suite_config", {})
        agent_config = params.get("agent_config", {})

        persona_configs = suite_config.get("persona_config", [])
        chaos_config = suite_config.get("chaos_profiles", {})
        judge_config = suite_config.get("judge_config", {})

        system_prompt = agent_config.get("system_prompt", "")
        model_name = agent_config.get("model_name", "unknown")
        endpoint_url = agent_config.get("endpoint_url")
        api_key = agent_config.get("api_key")

        logger.info("Generating personas from %d configs", len(persona_configs))
        person_generator = PersonaGenerator()
        profiles: list[PersonaProfile] = []
        for pc in persona_configs:
            if isinstance(pc, dict):
                profiles.append(PersonaProfile(
                    name=pc.get("name", "Unknown"),
                    category=PersonaCategory(pc.get("category", "standard")),
                    initial_user_intent=pc.get("initial_user_intent", "Generic inquiry"),
                    emotional_state=pc.get("emotional_state", "neutral"),
                    digital_literacy_score=pc.get("digital_literacy_score", 0.5),
                    edge_case_triggers=pc.get("edge_case_triggers", []),
                    conversation_turns=pc.get("conversation_turns", []),
                ))

        if not profiles:
            profiles = person_generator.get_builtin_profiles()
            logger.info("Using %d built-in personas", len(profiles))

        session_verdicts: list[SessionVerdict] = []
        chaos_profile = ChaosProfile.from_dict(chaos_config) if chaos_config else ChaosProfile()
        judge = LLMJudge()
        flusher = ClickHouseFlusher()

        for profile in profiles:
            logger.info("Evaluating persona: %s", profile.name)
            script = person_generator.generate_conversation_script(profile, MAX_TURNS_PER_SESSION)
            if endpoint_url:
                agent_provider = RemoteAgentProvider(
                    endpoint_url=endpoint_url,
                    api_key=api_key,
                    model_name=model_name,
                    system_prompt=system_prompt,
                )
            else:
                agent_provider = MockAgentProvider(system_prompt)
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
                session_id=f"{run_id}-{profile.name.lower().replace(' ', '-')}",
                persona_name=profile.name,
                turns=turns_data,
                context=system_prompt,
            )
            session_verdicts.append(session_verdict)
            await flusher.flush_turn_traces(
                organization_id=organization_id,
                run_id=run_id,
                session_id=session_verdict.session_id,
                persona_name=profile.name,
                turns=turns_data,
                turn_verdicts=session_verdict.turn_verdicts,
                chaos_log=chaos_log,
                model_name=model_name,
            )

        total_score = round(sum(sv.aggregate_score for sv in session_verdicts) / len(session_verdicts), 2) if session_verdicts else 0.0
        return {
            "run_id": run_id,
            "status": RunStatus.COMPLETED.value,
            "total_sessions": len(session_verdicts),
            "aggregate_score": total_score,
            "session_scores": [sv.aggregate_score for sv in session_verdicts],
        }



