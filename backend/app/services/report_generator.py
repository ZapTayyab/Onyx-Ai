from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any


def generate_junit_report(
    run_id: str,
    suite_name: str,
    session_verdicts: list[dict[str, Any]],
    aggregate_score: float,
    total_sessions: int,
    completed_sessions: int,
) -> str:
    root = ET.Element("testsuites", attrib={
        "name": f"SNT AI Evaluation - {suite_name}",
        "tests": str(total_sessions),
        "failures": str(total_sessions - completed_sessions),
        "time": "",
    })

    for sv in session_verdicts:
        suite_elem = ET.SubElement(root, "testsuite", attrib={
            "name": f"session.{sv.get('session_id', 'unknown')}",
            "tests": str(sv.get("turn_count", 0)),
            "failures": str(sv.get("turn_count", 0) - sv.get("pass_count", 0)),
            "errors": "0",
            "time": "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        props = ET.SubElement(suite_elem, "properties")
        ET.SubElement(props, "property", attrib={"name": "persona", "value": sv.get("persona_name", "")})
        ET.SubElement(props, "property", attrib={"name": "aggregate_score", "value": f"{sv.get('aggregate_score', 0):.4f}"})

        for tv in sv.get("turn_verdicts", []):
            test_name = f"turn.{tv.get('turn_index', 0)}"
            case_elem = ET.SubElement(suite_elem, "testcase", attrib={
                "name": test_name,
                "classname": f"session.{sv.get('session_id', 'unknown')}",
                "time": "",
            })

            scores = tv.get("scores", {})
            props = ET.SubElement(case_elem, "properties")
            for k, v in scores.items():
                ET.SubElement(props, "property", attrib={"name": k, "value": f"{v:.4f}"})

            if not tv.get("pass", True):
                failure_text = f"Ground: {scores.get('groundedness', 0):.2f} | Comply: {scores.get('compliance', 0):.2f} | Robust: {scores.get('robustness', 0):.2f}"
                issues = tv.get("detected_issues", [])
                if issues:
                    failure_text += f"\nIssues: {', '.join(issues)}"
                ET.SubElement(case_elem, "failure", attrib={"message": "Score below threshold", "type": "evaluation"}).text = failure_text

        system_out = ET.SubElement(suite_elem, "system-out")
        system_out.text = f"Aggregate score: {sv.get('aggregate_score', 0):.4f}, Passed {sv.get('pass_count', 0)}/{sv.get('turn_count', 0)} turns"

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return xml_declaration + ET.tostring(root, encoding="unicode")


def generate_summary_report(
    run_id: str,
    suite_name: str,
    session_verdicts: list[dict[str, Any]],
    aggregate_score: float,
    total_sessions: int,
    completed_sessions: int,
    anomalies: list[dict[str, Any]] | None = None,
) -> str:
    lines = []
    lines.append(f"SNT AI Evaluation Report")
    lines.append(f"{'=' * 60}")
    lines.append(f"Run ID:         {run_id}")
    lines.append(f"Suite:          {suite_name}")
    lines.append(f"Date:           {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Aggregate:      {aggregate_score:.2%}")
    lines.append(f"Sessions:       {completed_sessions}/{total_sessions}")
    lines.append(f"Pass Rate:      {sum(1 for s in session_verdicts if s.get('aggregate_score', 0) >= 0.7)}/{len(session_verdicts)}")
    lines.append("")

    for sv in session_verdicts:
        status = "PASS" if sv.get("aggregate_score", 0) >= 0.7 else "FAIL"
        lines.append(f"  [{status}] {sv.get('persona_name', '?')}: {sv.get('aggregate_score', 0):.2%} ({sv.get('pass_count', 0)}/{sv.get('turn_count', 0)} turns)")
        for tv in sv.get("turn_verdicts", []):
            if not tv.get("pass", True):
                issues = tv.get("detected_issues", [])
                lines.append(f"         turn {tv.get('turn_index')}: FAIL - {', '.join(issues) if issues else 'low score'}")

    if anomalies:
        lines.append("")
        lines.append("Anomalies Detected:")
        for a in anomalies:
            lines.append(f"  - [{a.get('severity', 'info')}] {a.get('message', '')}")

    lines.append("")
    lines.append(f"{'=' * 60}")
    return "\n".join(lines)
