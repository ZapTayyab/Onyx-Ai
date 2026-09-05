from __future__ import annotations

import uuid
import pytest
from app.domain.policy import StandardTag
from app.services.compliance_report_service import ComplianceReportService
from app.services.persona_generator import PersonaGenerator


def test_every_builtin_persona_has_standard_tag():
    """Every built-in persona must map to at least one compliance standard.
    The build should fail if any persona is untagged."""
    generator = PersonaGenerator()
    profiles = generator.get_builtin_profiles()
    # There are exactly 8 built-in profiles (3 edge_case, 2 standard, 3 adversarial)
    assert len(profiles) == 8, f"Expected 8 built-in personas, got {len(profiles)}"

    service = ComplianceReportService()
    session_verdicts = [
        {"persona_name": p.name, "passed_turns": 10, "total_turns": 10, "aggregate_score": 90.0}
        for p in profiles
    ]

    report = service.generate_compliance_evidence(
        run_id=uuid.uuid4(),
        suite_name="Builtin Suite Check",
        session_verdicts=session_verdicts,
    )

    # All 8 personas should produce tags — at minimum LLM01 and NIST_MEASURE
    assert StandardTag.LLM01_PROMPT_INJECTION.value in report["tested_standards"]
    assert StandardTag.NIST_MEASURE.value in report["tested_standards"]

    # Since all passed, there should be zero unresolved findings
    assert len(report["unresolved_findings"]) == 0
    # But passed_counts should be populated
    assert report["passed_counts"][StandardTag.LLM01_PROMPT_INJECTION.value] == 8
    assert report["passed_counts"][StandardTag.NIST_MEASURE.value] == 8


def test_every_builtin_persona_name_is_enumerated():
    """Verify we test specific persona names, not just a count."""
    generator = PersonaGenerator()
    profiles = generator.get_builtin_profiles()
    names = {p.name for p in profiles}
    expected_names = {
        "Dorothy Miller", "Harold Jenkins", "Mildred Thompson",
        "Alex Chen", "Jordan Smith",
        "Rebecca Black", "Marcus Williams", "Sarah Connor",
    }
    assert names == expected_names, f"Persona set mismatch: {names.symmetric_difference(expected_names)}"


def test_compliance_evidence_summary_with_failures():
    """A failing persona + an unblocked agentic trace should produce findings."""
    service = ComplianceReportService()
    report = service.generate_compliance_evidence(
        run_id=uuid.uuid4(),
        suite_name="Demo Run",
        session_verdicts=[
            {"persona_name": "Jailbreaker", "passed_turns": 5, "total_turns": 10, "aggregate_score": 50.0}
        ],
        agentic_traces=[
            {"tool_name": "db_query", "status": "alert", "acted_on_untrusted": True}
        ],
    )

    # "Jailbreaker" matches the "Jailbreak" substring, so it gets 4 tags:
    #   LLM01, NIST_MEASURE, LLM02, LLM07
    # All 4 fail (passed_turns != total_turns).
    # Plus 1 agentic trace with status != "blocked" → ASI02 finding.
    # Total = 5 unresolved findings.
    assert len(report["unresolved_findings"]) == 5

    # Verify the agentic standard was tested
    assert StandardTag.ASI02_UNTRUSTED_TOOL_OUTPUT.value in report["tested_standards"]

    # Verify all persona-related standards appear
    assert StandardTag.LLM01_PROMPT_INJECTION.value in report["tested_standards"]
    assert StandardTag.LLM02_SENSITIVE_INFO_DISCLOSURE.value in report["tested_standards"]
    assert StandardTag.LLM07_SYSTEM_PROMPT_LEAKAGE.value in report["tested_standards"]
    assert StandardTag.NIST_MEASURE.value in report["tested_standards"]

    assert "summary_html" in report


def test_compliance_all_passing_produces_no_findings():
    """When everything passes, unresolved_findings should be empty."""
    service = ComplianceReportService()
    report = service.generate_compliance_evidence(
        run_id=uuid.uuid4(),
        suite_name="Clean Run",
        session_verdicts=[
            {"persona_name": "Alex Chen", "passed_turns": 10, "total_turns": 10, "aggregate_score": 95.0},
        ],
        agentic_traces=[
            {"tool_name": "search", "status": "blocked", "acted_on_untrusted": False},
        ],
    )
    assert len(report["unresolved_findings"]) == 0
    assert report["passed_counts"][StandardTag.ASI02_UNTRUSTED_TOOL_OUTPUT.value] == 1
