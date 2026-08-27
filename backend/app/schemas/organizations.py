from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from app.config import BillingPlan


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    billing_plan: BillingPlan
    settings: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    name: str | None = None
    settings: str | None = None


class MemberResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteUserRequest(BaseModel):
    email: str
    role: str = "member"


class InviteUserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str


class BillingPlanUpdate(BaseModel):
    plan: BillingPlan


class UsageResponse(BaseModel):
    total_runs: int
    completed_runs: int
    failed_runs: int
    total_sessions: int
    active_members: int


class RunHistoryResponse(BaseModel):
    id: str
    suite_name: str
    status: str
    aggregate_score: float | None
    session_count: int
    started_at: datetime | None
    completed_at: datetime | None


class SSOConfigRequest(BaseModel):
    enabled: bool = True
    provider: str = "saml"
    domain: str | None = None
    metadata_url: str | None = None


class SSOConfigResponse(BaseModel):
    enabled: bool
    provider: str | None = None
    domain: str | None = None
    metadata_url: str | None = None
