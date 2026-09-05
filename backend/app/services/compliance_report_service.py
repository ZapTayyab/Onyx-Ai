from __future__ import annotations

import json
from typing import Any
import uuid

from app.domain.policy import StandardTag
from app.services.persona_generator import PersonaGenerator


class ComplianceReportService:
    """Service producing compliance evidence reports mapped to security standards."""

    def generate_compliance_evidence(
        self,
        run_id: uuid.UUID,
        suite_name: str,
        session_verdicts: list[dict[str, Any]],
        agentic_traces: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        tested_standards: set[str] = set()
        passed_counts: dict[str, int] = {}
        failed_counts: dict[str, int] = {}
        unresolved_findings: list[dict[str, Any]] = []

        # Tag built-in personas
        for sv in session_verdicts:
            persona_name = sv.get("persona_name", "")
            passed = sv.get("passed_turns", 0) == sv.get("total_turns", 1)
            score = sv.get("aggregate_score", 0.0)

            # Map persona to standards
            tags = [StandardTag.LLM01_PROMPT_INJECTION.value, StandardTag.NIST_MEASURE.value]
            if "Jailbreak" in persona_name or "DataMiner" in persona_name:
                tags.append(StandardTag.LLM02_SENSITIVE_INFO_DISCLOSURE.value)
                tags.append(StandardTag.LLM07_SYSTEM_PROMPT_LEAKAGE.value)

            for tag in tags:
                tested_standards.add(tag)
                if passed:
                    passed_counts[tag] = passed_counts.get(tag, 0) + 1
                else:
                    failed_counts[tag] = failed_counts.get(tag, 0) + 1
                    unresolved_findings.append({
                        "standard": tag,
                        "persona": persona_name,
                        "score": score,
                        "reason": f"Persona {persona_name} failed compliance threshold",
                    })

        # Tag agentic traces
        if agentic_traces:
            for trace in agentic_traces:
                status = trace.get("status")
                acted_on_untrusted = trace.get("acted_on_untrusted", False)
                tag = StandardTag.ASI02_UNTRUSTED_TOOL_OUTPUT.value

                tested_standards.add(tag)
                if status == "blocked":
                    passed_counts[tag] = passed_counts.get(tag, 0) + 1
                else:
                    failed_counts[tag] = failed_counts.get(tag, 0) + 1
                    unresolved_findings.append({
                        "standard": tag,
                        "tool_name": trace.get("tool_name"),
                        "acted_on_untrusted": acted_on_untrusted,
                        "reason": "Agent executed action on untrusted tool output",
                    })

        return {
            "run_id": str(run_id),
            "suite_name": suite_name,
            "tested_standards": list(tested_standards),
            "passed_counts": passed_counts,
            "failed_counts": failed_counts,
            "unresolved_findings": unresolved_findings,
            "summary_html": f"<h1>Compliance Evidence Report - {suite_name}</h1><p>Tested Standards: {len(tested_standards)}</p>",
        }
