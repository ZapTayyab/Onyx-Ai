from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import RunStatus, get_config
from app.core.clickhouse import clickhouse_mgr
from app.core.database import get_async_session
from app.core.security import TokenPayload, require_admin, require_member, verify_token
from app.core.temporal import get_temporal_client
from app.models.clickhouse.traces import (
    INSERT_TURN_TRACE,
    QUERY_AGGREGATE_METRICS_BY_RUN,
    QUERY_COMPLIANCE_BREAKDOWN,
    QUERY_REGRESSION_DELTA,
    QUERY_TRACES_BY_RUN,
)
from app.models.postgres import EvaluationSuite as EvaluationSuiteModel
from app.models.postgres import RunMetadata as RunMetadataModel
from app.models.postgres import TargetAgent as TargetAgentModel
from app.models.postgres import User as UserModel
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
    suite = await db.execute(
        select(EvaluationSuiteModel).where(
            EvaluationSuiteModel.id == body.suite_id,
            EvaluationSuiteModel.organization_id == payload.org_id,
        )
    )
    suite_entity = suite.scalar_one_or_none()
    if suite_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

    agent = await db.execute(
        select(TargetAgentModel).where(
            TargetAgentModel.id == body.agent_id,
            TargetAgentModel.organization_id == payload.org_id,
        )
    )
    agent_entity = agent.scalar_one_or_none()
    if agent_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    user_result = await db.execute(
        select(UserModel).where(UserModel.auth_provider_id == payload.sub)
    )
    user_entity = user_result.scalar_one_or_none()

    persona_list = suite_entity.persona_config or []
    run_meta = RunMetadataModel(
        organization_id=payload.org_id,
        suite_id=body.suite_id,
        agent_id=body.agent_id,
        status=RunStatus.PENDING,
        triggered_by=user_entity.id if user_entity else None,
        total_sessions=len(persona_list),
    )
    db.add(run_meta)
    await db.flush()
    await db.refresh(run_meta)

    runner = EvaluationRunner(temporal_client=get_temporal_client())
    asyncio.create_task(runner.run_via_temporal(
        organization_id=str(payload.org_id),
        suite_id=str(body.suite_id),
        agent_id=str(body.agent_id),
        run=run_meta,
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
        status=run_meta.status,
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
    offset = (page - 1) * per_page
    q = (
        select(RunMetadataModel)
        .where(RunMetadataModel.organization_id == payload.org_id)
        .offset(offset)
        .limit(per_page)
        .order_by(RunMetadataModel.created_at.desc())
    )
    result = await db.execute(q)
    runs = result.scalars().all()
    return [EvaluationStatusResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=EvaluationStatusResponse)
async def get_run_status(
    run_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> RunMetadataModel:
    result = await db.execute(
        select(RunMetadataModel).where(
            RunMetadataModel.id == run_id,
            RunMetadataModel.organization_id == payload.org_id,
        )
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


from fastapi.responses import PlainTextResponse

@router.get("/runs/{run_id}/report", response_class=PlainTextResponse)
async def get_run_report(
    run_id: uuid.UUID,
    format: str = Query("summary", pattern="^(summary|junit)$"),
    payload: TokenPayload = Depends(require_member),
    db: AsyncSession = Depends(get_async_session),
) -> str:
    result = await db.execute(
        select(RunMetadataModel, EvaluationSuiteModel)
        .join(EvaluationSuiteModel, RunMetadataModel.suite_id == EvaluationSuiteModel.id)
        .where(
            RunMetadataModel.id == run_id,
            RunMetadataModel.organization_id == payload.org_id,
        )
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
        
    run_meta, suite_entity = row
    
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
            suite_name=suite_entity.name,
            session_verdicts=session_verdicts_raw,
            aggregate_score=aggregate_score,
            total_sessions=run_meta.total_sessions,
            completed_sessions=run_meta.completed_sessions,
        )
    else:
        return generate_summary_report(
            run_id=str(run_meta.id),
            suite_name=suite_entity.name,
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
    rows = await clickhouse_mgr.execute(
        QUERY_TRACES_BY_RUN,
        {"organization_id": str(payload.org_id), "run_id": str(run_id)},
    )
    turns = []
    for row in rows:
        turns.append(
            TraceTurn(
                session_id=row[0],
                turn_id=row[1],
                timestamp=str(row[2]),
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
    return TraceQueryResponse(turns=turns, total=len(turns))


@router.get("/metrics/{run_id}", response_model=RunMetricsResponse)
async def get_run_metrics(
    run_id: uuid.UUID,
    payload: TokenPayload = Depends(require_member),
) -> RunMetricsResponse:
    rows = await clickhouse_mgr.execute(
        QUERY_AGGREGATE_METRICS_BY_RUN,
        {"organization_id": str(payload.org_id), "run_id": str(run_id)},
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No metrics found for this run")

    row = rows[0]
    return RunMetricsResponse(
        run_id=run_id,
        total_turns=row[1],
        avg_latency_ms=row[2],
        p50_latency_ms=row[3],
        p90_latency_ms=row[4],
        p99_latency_ms=row[5],
        total_tokens=row[6],
        avg_tokens_per_turn=row[7],
        total_sessions=row[8],
    )


@router.post("/regression-delta", response_model=RegressionDeltaResponse)
async def compute_regression_delta(
    body: RegressionDeltaRequest,
    payload: TokenPayload = Depends(require_member),
) -> RegressionDeltaResponse:
    rows = await clickhouse_mgr.execute(
        QUERY_REGRESSION_DELTA,
        {
            "current_run_id": str(body.current_run_id),
            "baseline_run_id": str(body.baseline_run_id),
        },
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not compute deltas")

    row = rows[0]
    deltas = [
        _build_delta_metric("Groundedness", row[0]),
        _build_delta_metric("Compliance", row[1]),
        _build_delta_metric("Robustness", row[2]),
        _build_delta_metric("P90 Latency", row[3]),
    ]
    return RegressionDeltaResponse(deltas=deltas)


def _build_delta_metric(name: str, raw_delta: float | None) -> DeltaMetric:
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
    suite = await db.execute(
        select(EvaluationSuiteModel).where(
            EvaluationSuiteModel.id == body.suite_id,
            EvaluationSuiteModel.organization_id == payload.org_id,
        )
    )
    suite_entity = suite.scalar_one_or_none()
    if suite_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

    agent = await db.execute(
        select(TargetAgentModel).where(
            TargetAgentModel.id == body.agent_id,
            TargetAgentModel.organization_id == payload.org_id,
        )
    )
    agent_entity = agent.scalar_one_or_none()
    if agent_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    persona_list = suite_entity.persona_config or []
    run_meta = RunMetadataModel(
        organization_id=payload.org_id,
        suite_id=body.suite_id,
        agent_id=body.agent_id,
        status=RunStatus.PENDING,
        triggered_by=payload.sub,
        total_sessions=len(persona_list),
    )
    db.add(run_meta)
    await db.flush()
    await db.refresh(run_meta)

    runner = EvaluationRunner()
    result = await runner.run_locally(
        organization_id=str(payload.org_id),
        suite_id=str(body.suite_id),
        agent_id=str(body.agent_id),
        run=run_meta,
        db=db,
    )

    from app.services.report_generator import generate_junit_report, generate_summary_report

    session_verdicts_raw = []
    if run_meta.summary_metrics:
        sessions_json = run_meta.summary_metrics.get("sessions", "[]")
        if isinstance(sessions_json, str):
            session_verdicts_raw = json.loads(sessions_json)
        else:
            session_verdicts_raw = sessions_json

    aggregate_score = run_meta.aggregate_score or 0.0
    report_junit = generate_junit_report(
        run_id=str(run_meta.id),
        suite_name=suite_entity.name,
        session_verdicts=session_verdicts_raw,
        aggregate_score=aggregate_score,
        total_sessions=run_meta.total_sessions,
        completed_sessions=run_meta.completed_sessions,
    )
    summary_text = generate_summary_report(
        run_id=str(run_meta.id),
        suite_name=suite_entity.name,
        session_verdicts=session_verdicts_raw,
        aggregate_score=aggregate_score,
        total_sessions=run_meta.total_sessions,
        completed_sessions=run_meta.completed_sessions,
    )

    logger.info(
        "Webhook evaluation complete: run=%s score=%s junit=%d chars",
        run_meta.id, aggregate_score, len(report_junit),
    )

    return WebhookEvalResponse(
        run_id=run_meta.id,
        status=run_meta.status,
        suite_name=suite_entity.name,
        aggregate_score=aggregate_score,
        total_sessions=run_meta.total_sessions,
        completed_sessions=run_meta.completed_sessions,
        summary={"report": summary_text},
        report_junit=report_junit,
    )
