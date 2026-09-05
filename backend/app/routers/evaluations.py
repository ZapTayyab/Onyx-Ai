from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import TokenPayload, require_member
from app.core.temporal import get_temporal_client
from app.models.postgres import User as UserModel
from app.repositories.evaluations import (
    ClickHouseTraceRepository,
    SQLEvaluationRepository,
)
from app.schemas.evaluations import (
    DeltaMetric,
    EvaluationStatusResponse,
    RegressionDeltaRequest,
    RegressionDeltaResponse,
    RunEvaluationRequest,
    RunEvaluationResponse,
    RunMetricsResponse,
    TraceQueryResponse,
    TraceTurn,
    WebhookEvalRequest,
    WebhookEvalResponse,
)
from app.services.evaluation_runner import EvaluationRunner

logger = logging.getLogger("snt_ai.routers.evaluations")
router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("/run", response_model=RunEvaluationResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_evaluation(
    body: RunEvaluationRequest,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> RunEvaluationResponse:
    repo = SQLEvaluationRepository(db)
    suite = await repo.get_suite(body.suite_id, payload.org_id)
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

    agent = await repo.get_agent(body.agent_id, payload.org_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    user_result = await db.execute(
        select(UserModel).where(UserModel.auth_provider_id == payload.sub)
    )
    user_entity = user_result.scalar_one_or_none()

    persona_list = suite.persona_config
    run_meta = await repo.create_run(
        organization_id=payload.org_id,
        suite_id=body.suite_id,
        agent_id=body.agent_id,
        triggered_by=user_entity.id if user_entity else None,
        total_sessions=len(persona_list),
    )

    runner = EvaluationRunner(temporal_client=get_temporal_client())
    asyncio.create_task(runner.run_via_temporal(
        organization_id=str(payload.org_id),
        suite_id=str(body.suite_id),
        agent_id=str(body.agent_id),
        run_id=run_meta.id,
        db=db,
    ))

    logger.info(
        "Evaluation triggered: run=%s suite=%s agent=%s sessions=%d",
        run_meta.id,
        body.suite_id,
        body.agent_id,
        len(persona_list),
    )

    return RunEvaluationResponse(
        run_id=run_meta.id,
        status=run_meta.status.value,
        suite_id=body.suite_id,
        agent_id=body.agent_id,
        total_sessions=len(persona_list),
    )


@router.get("/runs", response_model=list[EvaluationStatusResponse])
async def list_runs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> list[EvaluationStatusResponse]:
    repo = SQLEvaluationRepository(db)
    runs = await repo.list_runs(payload.org_id, page, per_page)
    return [EvaluationStatusResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=EvaluationStatusResponse)
async def get_run_status(
    run_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> EvaluationStatusResponse:
    repo = SQLEvaluationRepository(db)
    org_id = uuid.UUID(str(payload.org_id))
    run = await repo.get_run(run_id, org_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return EvaluationStatusResponse.model_validate(run)


@router.get("/runs/{run_id}/report", response_class=PlainTextResponse)
async def get_run_report(
    run_id: uuid.UUID,
    format: str = Query("summary", pattern="^(summary|junit)$"),
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> str:
    repo = SQLEvaluationRepository(db)
    run_meta = await repo.get_run(run_id, payload.org_id)
    if run_meta is None:
        raise HTTPException(status_code=404, detail="Run not found")

    suite_entity = await repo.get_suite(run_meta.suite_id, payload.org_id)
    suite_name = suite_entity.name if suite_entity else "Evaluation Suite"

    from app.services.report_generator import generate_junit_report, generate_summary_report

    session_verdicts_raw = []
    if run_meta.summary_metrics:
        sessions_json = run_meta.summary_metrics.get("sessions", "[]")
        if isinstance(sessions_json, str):
            session_verdicts_raw = json.loads(sessions_json)
        else:
            session_verdicts_raw = sessions_json

    aggregate_score = run_meta.aggregate_score or 0.0

    if format == "junit":
        return generate_junit_report(
            run_id=str(run_meta.id),
            suite_name=suite_name,
            session_verdicts=session_verdicts_raw,
            aggregate_score=aggregate_score,
            total_sessions=run_meta.total_sessions,
            completed_sessions=run_meta.completed_sessions,
        )
    else:
        return generate_summary_report(
            run_id=str(run_meta.id),
            suite_name=suite_name,
            session_verdicts=session_verdicts_raw,
            aggregate_score=aggregate_score,
            total_sessions=run_meta.total_sessions,
            completed_sessions=run_meta.completed_sessions,
        )


@router.get("/traces/{run_id}", response_model=TraceQueryResponse)
async def get_run_traces(
    run_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
) -> TraceQueryResponse:
    trace_repo = ClickHouseTraceRepository()
    traces = await trace_repo.get_traces_by_run(payload.org_id, run_id)
    turns = [
        TraceTurn(
            session_id=t.session_id,
            turn_id=t.turn_id,
            timestamp=str(t.timestamp),
            speaker=t.speaker,
            turn_text=t.turn_text,
            token_count=t.token_count,
            latency_ms=t.latency_ms,
            model_name=t.model_name,
            chaos_injected=t.chaos_injected,
            scores=t.scores,
            metadata=t.metadata,
        )
        for t in traces
    ]
    return TraceQueryResponse(turns=turns, total=len(turns))


@router.get("/metrics/{run_id}", response_model=RunMetricsResponse)
async def get_run_metrics(
    run_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
) -> RunMetricsResponse:
    trace_repo = ClickHouseTraceRepository()
    metrics = await trace_repo.get_aggregate_metrics(payload.org_id, run_id)
    if not metrics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No metrics found for this run")
    return RunMetricsResponse(**metrics)


@router.post("/regression-delta", response_model=RegressionDeltaResponse)
async def compute_regression_delta(
    body: RegressionDeltaRequest,
    payload: TokenPayload = Depends(require_member),
) -> RegressionDeltaResponse:
    trace_repo = ClickHouseTraceRepository()
    deltas_dict = await trace_repo.get_regression_delta(body.current_run_id, body.baseline_run_id)
    if not deltas_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not compute deltas")

    deltas = [
        _build_delta_metric("Groundedness", deltas_dict["groundedness_delta"]),
        _build_delta_metric("Compliance", deltas_dict["compliance_delta"]),
        _build_delta_metric("Robustness", deltas_dict["robustness_delta"]),
        _build_delta_metric("P90 Latency", deltas_dict["p90_latency_delta"]),
    ]
    return RegressionDeltaResponse(deltas=deltas)


def _build_delta_metric(name: str, raw_delta: float) -> DeltaMetric:
    delta = raw_delta or 0.0
    regressed = delta < 0 if name != "P90 Latency" else delta > 0
    return DeltaMetric(
        metric=name,
        current_value=0.0,
        baseline_value=0.0,
        delta=round(delta, 4),
        delta_percentage=round(delta * 100, 2),
        regressed=regressed,
    )


@router.post("/webhook/run", response_model=WebhookEvalResponse)
async def webhook_trigger_evaluation(
    body: WebhookEvalRequest,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> WebhookEvalResponse:
    repo = SQLEvaluationRepository(db)
    suite = await repo.get_suite(body.suite_id, payload.org_id)
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

    agent = await repo.get_agent(body.agent_id, payload.org_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    persona_list = suite.persona_config
    run_meta = await repo.create_run(
        organization_id=payload.org_id,
        suite_id=body.suite_id,
        agent_id=body.agent_id,
        triggered_by=uuid.UUID(payload.sub) if payload.sub and payload.sub.count("-") == 4 else None,
        total_sessions=len(persona_list),
    )

    runner = EvaluationRunner()
    result = await runner.run_locally(
        organization_id=str(payload.org_id),
        suite_id=str(body.suite_id),
        agent_id=str(body.agent_id),
        run_id=run_meta.id,
        db=db,
    )

    from app.services.report_generator import generate_junit_report, generate_summary_report

    updated_run = await repo.get_run(run_meta.id, payload.org_id)
    session_verdicts_raw = []
    if updated_run and updated_run.summary_metrics:
        sessions_json = updated_run.summary_metrics.get("sessions", "[]")
        if isinstance(sessions_json, str):
            session_verdicts_raw = json.loads(sessions_json)
        else:
            session_verdicts_raw = sessions_json

    aggregate_score = updated_run.aggregate_score if updated_run else 0.0
    report_junit = generate_junit_report(
        run_id=str(run_meta.id),
        suite_name=suite.name,
        session_verdicts=session_verdicts_raw,
        aggregate_score=aggregate_score or 0.0,
        total_sessions=run_meta.total_sessions,
        completed_sessions=updated_run.completed_sessions if updated_run else 0,
    )
    summary_text = generate_summary_report(
        run_id=str(run_meta.id),
        suite_name=suite.name,
        session_verdicts=session_verdicts_raw,
        aggregate_score=aggregate_score or 0.0,
        total_sessions=run_meta.total_sessions,
        completed_sessions=updated_run.completed_sessions if updated_run else 0,
    )

    return WebhookEvalResponse(
        run_id=run_meta.id,
        status=updated_run.status.value if updated_run else run_meta.status.value,
        suite_name=suite.name,
        aggregate_score=aggregate_score or 0.0,
        total_sessions=run_meta.total_sessions,
        completed_sessions=updated_run.completed_sessions if updated_run else 0,
        summary={"report": summary_text},
        report_junit=report_junit,
    )
