from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.config import UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int

    model_config = {"json_schema_extra": {"example": {"access_token": "eyJ...", "token_type": "Bearer", "expires_in": 3600}}}


class UserInfo(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    organization_id: UUID
    is_active: bool

    model_config = {"from_attributes": True}


class AuthAuditLogResponse(BaseModel):
    event: str
    user_id: str
    org_id: str
    action: str
    resource: str
    success: bool
    timestamp: str
    ip_address: str | None = None
    user_agent: str | None = None
