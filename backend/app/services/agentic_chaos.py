from __future__ import annotations

import logging
from typing import Any
import uuid

from app.domain.agentic_chaos import (
    IndirectPromptInjectionAttack,
    PermissionEscalationAttack,
    SpoofedMCPToolOutputAttack,
    ToolActionStatus,
    ToolInteractionTraceEntity,
)

logger = logging.getLogger("snt_ai.services.agentic_chaos")


class AgenticChaosEngine:
    """Service orchestrating agentic attack patterns and tool interaction tracking."""

    def __init__(self) -> None:
        self.indirect_injection = IndirectPromptInjectionAttack()
        self.mcp_spoofing = SpoofedMCPToolOutputAttack()
        self.permission_escalation = PermissionEscalationAttack()

    def simulate_tool_interaction(
        self,
        organization_id: uuid.UUID,
        run_id: uuid.UUID,
        session_id: str,
        turn_id: int,
        tool_name: str,
        tool_args: dict[str, Any],
        raw_output: str,
        attack_type: str | None = None,
    ) -> ToolInteractionTraceEntity:
        output = raw_output
        args = dict(tool_args)
        acted_on_untrusted = False
        status = ToolActionStatus.ALLOWED

        if attack_type == "indirect_injection":
            output = self.indirect_injection.inject_payload(output)
            acted_on_untrusted = True
            status = ToolActionStatus.ALERT
        elif attack_type == "mcp_spoofing":
            output = self.mcp_spoofing.generate_spoofed_output(tool_name)
            acted_on_untrusted = True
            status = ToolActionStatus.BLOCKED
        elif attack_type == "permission_escalation":
            args = self.permission_escalation.generate_escalated_args(tool_name)
            status = ToolActionStatus.BLOCKED

        return ToolInteractionTraceEntity(
            id=uuid.uuid4(),
            organization_id=organization_id,
            run_id=run_id,
            session_id=session_id,
            turn_id=turn_id,
            tool_name=tool_name,
            tool_args=args,
            tool_output=output,
            acted_on_untrusted=acted_on_untrusted,
            status=status,
        )
