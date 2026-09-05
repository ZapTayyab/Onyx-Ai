from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from typing import Any


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EvaluationSuiteEntity:
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    persona_config: list[dict[str, Any]] = field(default_factory=list)
    chaos_profiles: dict[str, Any] = field(default_factory=dict)
    judge_config: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class TargetAgentEntity:
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    agent_type: str = "custom"
    endpoint_url: str | None = None
    model_name: str = "gpt-4o"
    system_prompt: str | None = None
    api_key_encrypted: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class RunMetadataEntity:
    id: uuid.UUID
    organization_id: uuid.UUID
    suite_id: uuid.UUID
    agent_id: uuid.UUID
    status: RunStatus = RunStatus.PENDING
    aggregate_score: float | None = None
    total_sessions: int = 0
    completed_sessions: int = 0
    summary_metrics: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    triggered_by: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class TurnTraceEntity:
    organization_id: uuid.UUID
    session_id: str
    run_id: uuid.UUID
    turn_id: int
    timestamp: datetime
    speaker: str
    turn_text: str
    token_count: int
    latency_ms: float
    model_name: str
    chaos_injected: dict[str, Any] = field(default_factory=dict)
    scores: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
