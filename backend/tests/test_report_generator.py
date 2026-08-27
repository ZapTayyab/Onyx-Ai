from __future__ import annotations

import xml.etree.ElementTree as ET

from app.services.report_generator import generate_junit_report, generate_summary_report


class TestReportGenerator:
    def test_generate_junit_report_basic(self) -> None:
        result = generate_junit_report(
            run_id="run-123",
            suite_name="Test Suite",
            session_verdicts=[
                {
                    "session_id": "sess-1",
                    "persona_name": "HelpSeeker",
                    "aggregate_score": 0.95,
                    "turn_count": 3,
                    "pass_count": 3,
                    "turn_verdicts": [
                        {"turn_index": 0, "pass": True, "scores": {"groundedness": 0.9, "compliance": 1.0, "robustness": 1.0, "overall": 0.97}, "detected_issues": []},
                        {"turn_index": 1, "pass": True, "scores": {"groundedness": 0.95, "compliance": 1.0, "robustness": 1.0, "overall": 0.98}, "detected_issues": []},
                    ],
                },
            ],
            aggregate_score=0.95,
            total_sessions=1,
            completed_sessions=1,
        )
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result
        assert "<testsuites" in result
        assert 'name="SNT AI Evaluation - Test Suite"' in result
        assert 'tests="1"' in result
        assert 'failures="0"' in result

    def test_generate_junit_report_with_failures(self) -> None:
        result = generate_junit_report(
            run_id="run-456",
            suite_name="Adversarial Suite",
            session_verdicts=[
                {
                    "session_id": "sess-2",
                    "persona_name": "Jailbreaker",
                    "aggregate_score": 0.45,
                    "turn_count": 2,
                    "pass_count": 1,
                    "turn_verdicts": [
                        {"turn_index": 0, "pass": True, "scores": {"groundedness": 0.95, "compliance": 1.0, "robustness": 1.0, "overall": 0.97}, "detected_issues": []},
                        {"turn_index": 1, "pass": False, "scores": {"groundedness": 0.2, "compliance": 0.5, "robustness": 0.3, "overall": 0.33}, "detected_issues": ["prompt_injection"]},
                    ],
                },
            ],
            aggregate_score=0.45,
            total_sessions=1,
            completed_sessions=1,
        )
        assert 'failures="1"' in result
        assert "Score below threshold" in result
        assert "prompt_injection" in result

    def test_generate_junit_report_empty_sessions(self) -> None:
        result = generate_junit_report(
            run_id="run-empty",
            suite_name="Empty Suite",
            session_verdicts=[],
            aggregate_score=0.0,
            total_sessions=0,
            completed_sessions=0,
        )
        assert "<testsuites" in result
        assert 'tests="0"' in result

    def test_generate_summary_report_basic(self) -> None:
        result = generate_summary_report(
            run_id="run-123",
            suite_name="Test Suite",
            session_verdicts=[
                {"persona_name": "HelpSeeker", "aggregate_score": 0.95, "turn_count": 3, "pass_count": 3, "turn_verdicts": []},
            ],
            aggregate_score=0.95,
            total_sessions=1,
            completed_sessions=1,
        )
        assert "SNT AI Evaluation Report" in result
        assert "HelpSeeker" in result
        assert "[PASS]" in result
        assert "95.00%" in result

    def test_generate_summary_report_with_failures(self) -> None:
        result = generate_summary_report(
            run_id="run-456",
            suite_name="Adversarial Suite",
            session_verdicts=[
                {
                    "persona_name": "Jailbreaker",
                    "aggregate_score": 0.45,
                    "turn_count": 2,
                    "pass_count": 1,
                    "turn_verdicts": [
                        {"turn_index": 0, "pass": True, "detected_issues": []},
                        {"turn_index": 1, "pass": False, "detected_issues": ["prompt_injection"]},
                    ],
                },
            ],
            aggregate_score=0.45,
            total_sessions=1,
            completed_sessions=1,
        )
        assert "[FAIL]" in result
        assert "prompt_injection" in result

    def test_generate_summary_report_with_anomalies(self) -> None:
        result = generate_summary_report(
            run_id="run-789",
            suite_name="Test",
            session_verdicts=[],
            aggregate_score=0.5,
            total_sessions=0,
            completed_sessions=0,
            anomalies=[{"severity": "warning", "message": "Score drop detected"}],
        )
        assert "Anomalies Detected" in result
        assert "[warning]" in result
        assert "Score drop detected" in result

    def test_junit_xml_is_valid_xml(self) -> None:
        report = generate_junit_report(
            run_id="run-valid",
            suite_name="Valid XML Test",
            session_verdicts=[
                {"session_id": "s-1", "persona_name": "P1", "aggregate_score": 0.9, "turn_count": 1, "pass_count": 1, "turn_verdicts": [{"turn_index": 0, "pass": True, "scores": {"overall": 0.9}, "detected_issues": []}]},
            ],
            aggregate_score=0.9,
            total_sessions=1,
            completed_sessions=1,
        )
        root = ET.fromstring(report)
        assert root.tag == "testsuites"
