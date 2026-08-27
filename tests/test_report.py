from stress_test_engine import generate_report_string


def test_generate_report_string_includes_summary_sections():
    report = generate_report_string(
        [
            {
                "customer_name": "Test User",
                "session_id": "session-1",
                "emotional_state": "Furious",
                "account_tier": "Free",
                "session_failed": True,
                "turn_results": [
                    {
                        "turn_id": 1,
                        "user_text": "hello",
                        "passed": False,
                        "reason": "POLITENESS_FAIL [politeness]: Bot lost corporate tone under user aggression",
                    }
                ],
            }
        ]
    )
    assert "Executive Summary" in report
    assert "Session Details" in report
    assert "Test User" in report
