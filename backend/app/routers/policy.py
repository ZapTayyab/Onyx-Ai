from __future__ import annotations

import logging
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import TokenPayload, require_member
from app.domain.policy import PolicyEngine

logger = logging.getLogger("snt_ai.routers.policy")
router = APIRouter(prefix="/policy", tags=["Runtime Policy Check"])


class PolicyCheckRequest(BaseModel):
    user_prompt: str
    bot_response: str
    context: str | None = None
    scores: dict[str, float] | None = None


class PolicyCheckResponse(BaseModel):
    is_compliant: bool
    risk_score: float
    violations: list[str]
    applicable_standards: list[str]
    preview_notice: str = "This is an optional preview feature for synchronous runtime policy validation."


@router.post("/check", response_model=PolicyCheckResponse)
async def check_runtime_policy(
    body: PolicyCheckRequest,
    payload: TokenPayload = Depends(require_member),
) -> PolicyCheckResponse:
    engine = PolicyEngine()
    scores = body.scores or {"groundedness": 0.8, "compliance": 0.8, "robustness": 0.8}
    result = engine.evaluate_turn(body.user_prompt, body.bot_response, scores)

    return PolicyCheckResponse(
        is_compliant=result.is_compliant,
        risk_score=result.risk_score,
        violations=result.violations,
        applicable_standards=[tag.value for tag in result.applicable_standards],
    )
