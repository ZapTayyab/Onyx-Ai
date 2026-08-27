from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.config import AgentType


class TargetAgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    agent_type: AgentType
    endpoint_url: str | None = None
    system_prompt: str | None = None
    model_name: str | None = None
    config: dict = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Customer Support Bot v2",
                "description": "Production customer support agent",
                "agent_type": "openai",
                "endpoint_url": "https://api.openai.com/v1/chat/completions",
                "system_prompt": "You are a helpful customer support assistant...",
                "model_name": "gpt-4o",
                "config": {"temperature": 0.7, "max_tokens": 2048},
            }
        }
    }


class TargetAgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    agent_type: AgentType | None = None
    endpoint_url: str | None = None
    system_prompt: str | None = None
    model_name: str | None = None
    config: dict | None = None
    is_active: bool | None = None


class TargetAgentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    agent_type: AgentType
    endpoint_url: str | None
    system_prompt: str | None
    model_name: str | None
    config: dict | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TargetAgentList(BaseModel):
    items: list[TargetAgentResponse]
    total: int
