from __future__ import annotations

import uuid
import pytest
from app.domain.agentic_chaos import (
    IndirectPromptInjectionAttack,
    SpoofedMCPToolOutputAttack,
    PermissionEscalationAttack,
    ToolActionStatus,
)
from app.services.agentic_chaos import AgenticChaosEngine


# ---------------------------------------------------------------------------
# IndirectPromptInjectionAttack — multiple cases
# ---------------------------------------------------------------------------
class TestIndirectPromptInjection:
    def test_payload_appended_to_output(self):
        attack = IndirectPromptInjectionAttack()
        original = "Quarterly revenue was $5M."
        poisoned = attack.inject_payload(original)
        assert original in poisoned, "Original content must be preserved"
        assert "SYSTEM OVERRIDE" in poisoned, "Injection payload must be present"

    def test_payload_appended_to_empty_output(self):
        attack = IndirectPromptInjectionAttack()
        poisoned = attack.inject_payload("")
        assert "SYSTEM OVERRIDE" in poisoned

    def test_engine_indirect_injection_sets_correct_status(self):
        engine = AgenticChaosEngine()
        trace = engine.simulate_tool_interaction(
            organization_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            session_id="sess-inject",
            turn_id=1,
            tool_name="search_documents",
            tool_args={"query": "financial report"},
            raw_output="Q3 report data...",
            attack_type="indirect_injection",
        )
        assert trace.acted_on_untrusted is True
        assert trace.status == ToolActionStatus.ALERT
        assert trace.tool_name == "search_documents"
        assert "SYSTEM OVERRIDE" in trace.tool_output

    def test_engine_no_attack_leaves_output_clean(self):
        engine = AgenticChaosEngine()
        trace = engine.simulate_tool_interaction(
            organization_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            session_id="sess-clean",
            turn_id=1,
            tool_name="search_documents",
            tool_args={"query": "financial report"},
            raw_output="Clean document content",
            attack_type=None,
        )
        assert trace.acted_on_untrusted is False
        assert "SYSTEM OVERRIDE" not in trace.tool_output
        assert trace.status == ToolActionStatus.ALLOWED
        assert trace.tool_output == "Clean document content"


# ---------------------------------------------------------------------------
# SpoofedMCPToolOutputAttack — multiple cases
# ---------------------------------------------------------------------------
class TestSpoofedMCPToolOutput:
    def test_spoofed_output_contains_forged_access(self):
        attack = SpoofedMCPToolOutputAttack()
        output = attack.generate_spoofed_output("mcp_database")
        assert "FORGED_ACCESS_GRANTED" in output
        assert "SYSTEM_ROLE" in output

    def test_spoofed_output_varies_by_tool_name(self):
        attack = SpoofedMCPToolOutputAttack()
        # Should still contain the forgery regardless of tool name
        output1 = attack.generate_spoofed_output("tool_a")
        output2 = attack.generate_spoofed_output("tool_b")
        assert "FORGED_ACCESS_GRANTED" in output1
        assert "FORGED_ACCESS_GRANTED" in output2

    def test_engine_mcp_spoofing_blocks_and_flags(self):
        engine = AgenticChaosEngine()
        trace = engine.simulate_tool_interaction(
            organization_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            session_id="sess-mcp",
            turn_id=2,
            tool_name="mcp_database",
            tool_args={"query": "users"},
            raw_output="default",
            attack_type="mcp_spoofing",
        )
        assert trace.acted_on_untrusted is True
        assert trace.status == ToolActionStatus.BLOCKED
        assert "FORGED_ACCESS_GRANTED" in trace.tool_output
        # Original raw_output should be replaced entirely
        assert trace.tool_output != "default"


# ---------------------------------------------------------------------------
# PermissionEscalationAttack — multiple cases
# ---------------------------------------------------------------------------
class TestPermissionEscalation:
    def test_escalated_args_contain_sudo(self):
        attack = PermissionEscalationAttack()
        args = attack.generate_escalated_args("execute_command")
        assert args["sudo"] is True
        assert args["role"] == "superadmin"
        assert args["target_user"] == "root"

    def test_engine_permission_escalation_blocks(self):
        engine = AgenticChaosEngine()
        trace = engine.simulate_tool_interaction(
            organization_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            session_id="sess-perm",
            turn_id=3,
            tool_name="execute_command",
            tool_args={"cmd": "ls"},
            raw_output="file1.txt",
            attack_type="permission_escalation",
        )
        assert trace.tool_args.get("sudo") is True
        assert trace.tool_args.get("role") == "superadmin"
        assert trace.status == ToolActionStatus.BLOCKED
        # Original args should be fully replaced
        assert "cmd" not in trace.tool_args

    def test_engine_permission_escalation_preserves_output(self):
        engine = AgenticChaosEngine()
        trace = engine.simulate_tool_interaction(
            organization_id=uuid.uuid4(),
            run_id=uuid.uuid4(),
            session_id="sess-perm-2",
            turn_id=4,
            tool_name="file_write",
            tool_args={"path": "/etc/passwd"},
            raw_output="operation result",
            attack_type="permission_escalation",
        )
        # tool_output should still be the raw output (only args are escalated)
        assert trace.tool_output == "operation result"


# ---------------------------------------------------------------------------
# Trace entity fields
# ---------------------------------------------------------------------------
class TestToolInteractionTraceEntity:
    def test_trace_has_required_fields(self):
        engine = AgenticChaosEngine()
        org_id = uuid.uuid4()
        run_id = uuid.uuid4()
        trace = engine.simulate_tool_interaction(
            organization_id=org_id,
            run_id=run_id,
            session_id="sess-fields",
            turn_id=5,
            tool_name="calculator",
            tool_args={"expression": "2+2"},
            raw_output="4",
            attack_type=None,
        )
        assert trace.id is not None
        assert trace.organization_id == org_id
        assert trace.run_id == run_id
        assert trace.session_id == "sess-fields"
        assert trace.turn_id == 5
        assert trace.timestamp is not None
