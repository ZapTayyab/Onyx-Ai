from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.config import RunStatus


class RunEvaluationRequest(BaseModel):
    suite_id: uuid.UUID
    agent_id: uuid.UUID
    description: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "suite_id": "550e8400-e29b-41d4-a716-446655440000",
                "agent_id": "550e8400-e29b-41d4-a716-446655440001",
                "description": "Weekly regression run",
            }
        }
    }


class RunEvaluationResponse(BaseModel):
    run_id: uuid.UUID
    status: RunStatus
    suite_id: uuid.UUID
    agent_id: uuid.UUID
    total_sessions: int

    model_config = {"json_schema_extra": {"example": {"run_id": "550e8400-...", "status": "pending", "suite_id": "550e8400-...", "agent_id": "550e8400-...", "total_sessions": 5}}}


class EvaluationStatusResponse(BaseModel):
    id: uuid.UUID
    status: RunStatus
    total_sessions: int
    completed_sessions: int
    aggregate_score: float | None
    summary_metrics: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RegressionDeltaRequest(BaseModel):
    current_run_id: uuid.UUID
    baseline_run_id: uuid.UUID


class DeltaMetric(BaseModel):
    metric: str
    current_value: float
    baseline_value: float
    delta: float
    delta_percentage: float
    regressed: bool


class RegressionDeltaResponse(BaseModel):
    deltas: list[DeltaMetric]


class TraceTurn(BaseModel):
    session_id: str
    turn_id: int
    timestamp: str
    speaker: str
    turn_text: str
    token_count: int
    latency_ms: float
    model_name: str
    chaos_injected: dict
    scores: dict
    metadata: dict


class TraceQueryResponse(BaseModel):
    turns: list[TraceTurn]
    total: int


class RunMetricsResponse(BaseModel):
    run_id: uuid.UUID
    total_turns: int
    avg_latency_ms: float
    p50_latency_ms: float
    p90_latency_ms: float
    p99_latency_ms: float
    total_tokens: int
    avg_tokens_per_turn: float
    total_sessions: int


class WebhookEvalRequest(RunEvaluationRequest):
    source: str = "github-actions"
    branch: str | None = None
    commit_sha: str | None = None
    pr_number: int | None = None


class WebhookEvalResponse(BaseModel):
    run_id: uuid.UUID
    status: RunStatus
    suite_name: str
    aggregate_score: float
    total_sessions: int
    completed_sessions: int
    summary: dict
    report_junit: str
