from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EvaluationSuiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    persona_config: list[dict] = Field(default_factory=list)
    chaos_profiles: dict = Field(default_factory=dict)
    judge_config: dict = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Red Team Suite v1",
                "description": "Adversarial testing scenarios",
                "persona_config": [
                    {
                        "name": "Confused Elderly User",
                        "category": "edge_case",
                        "system_prompt_override": None,
                        "edge_case_triggers": ["I don't understand", "Can you repeat that?"],
                    }
                ],
                "chaos_profiles": {
                    "network_latency": {"enabled": True, "mean_ms": 500, "std_ms": 100},
                    "context_bloat": {"enabled": False},
                    "guardrail_interruption": {"enabled": True, "probability": 0.1},
                },
                "judge_config": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "rubrics": ["groundedness", "compliance", "robustness"],
                },
            }
        }
    }


class EvaluationSuiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    persona_config: list[dict] | None = None
    chaos_profiles: dict | None = None
    judge_config: dict | None = None
    is_active: bool | None = None


class EvaluationSuiteResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    persona_config: list[dict]
    chaos_profiles: dict | None
    judge_config: dict | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvaluationSuiteList(BaseModel):
    items: list[EvaluationSuiteResponse]
    total: int
