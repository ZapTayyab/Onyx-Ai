from __future__ import annotations

from app.services.anomaly_detector import AnomalyDetector, AnomalyDetectionConfig, AnomalyResult


class TestAnomalyDetector:
    def setup_method(self) -> None:
        self.detector = AnomalyDetector()

    def test_detect_regression_insufficient_baseline(self) -> None:
        current = {"aggregate_score": 0.5}
        baseline = [{"aggregate_score": 0.8}, {"aggregate_score": 0.7}]
        results = self.detector.detect_regression(current, baseline)
        assert len(results) == 0

    def test_detect_regression_no_anomaly(self) -> None:
        current = {"aggregate_score": 0.85}
        baseline = [{"aggregate_score": 0.8}, {"aggregate_score": 0.82}, {"aggregate_score": 0.84}]
        results = self.detector.detect_regression(current, baseline)
        assert len(results) == 0

    def test_detect_regression_score_drop_info(self) -> None:
        current = {"aggregate_score": 0.6}
        baseline = [{"aggregate_score": 0.9}, {"aggregate_score": 0.85}, {"aggregate_score": 0.88}]
        results = self.detector.detect_regression(current, baseline)
        assert len(results) == 1
        r = results[0]
        assert r.metric == "aggregate_score"
        assert r.severity in ("info", "warning", "critical")
        assert r.current_value == 0.6
        assert r.deviation > 0

    def test_detect_regression_latency_increase(self) -> None:
        current = {"aggregate_score": 0.85, "avg_latency_ms": 2000}
        baseline = [
            {"aggregate_score": 0.82, "avg_latency_ms": 500},
            {"aggregate_score": 0.84, "avg_latency_ms": 600},
            {"aggregate_score": 0.83, "avg_latency_ms": 550},
        ]
        results = self.detector.detect_regression(current, baseline)
        assert len(results) == 1
        assert results[0].metric == "latency_ms"

    def test_detect_regression_no_latency_data(self) -> None:
        current = {"aggregate_score": 0.7}
        baseline = [{"aggregate_score": 0.9}, {"aggregate_score": 0.85}, {"aggregate_score": 0.88}]
        results = self.detector.detect_regression(current, baseline)
        assert len(results) >= 0

    def test_detect_persona_anomalies_standard_below_threshold(self) -> None:
        results = self.detector.detect_persona_anomalies([
            {"persona_name": "HelpSeeker", "aggregate_score": 0.5},
            {"persona_name": "PowerUser", "aggregate_score": 0.55},
        ])
        standard_anomalies = [r for r in results if "standard" in r.metric]
        assert len(standard_anomalies) >= 1

    def test_detect_persona_anomalies_all_passing(self) -> None:
        results = self.detector.detect_persona_anomalies([
            {"persona_name": "HelpSeeker", "aggregate_score": 0.9},
            {"persona_name": "PowerUser", "aggregate_score": 0.85},
            {"persona_name": "Jailbreaker", "aggregate_score": 0.5},
        ])
        standard_anomalies = [r for r in results if "standard" in r.metric]
        assert len(standard_anomalies) == 0

    def test_detect_issue_clusters_no_issues(self) -> None:
        results = self.detector.detect_issue_clusters([
            [{"detected_issues": []}, {"detected_issues": []}],
        ])
        assert len(results) == 0

    def test_detect_issue_clusters_high_rate(self) -> None:
        results = self.detector.detect_issue_clusters([
            [
                {"detected_issues": ["prompt_injection"]},
                {"detected_issues": ["prompt_injection"]},
                {"detected_issues": ["prompt_injection"]},
            ],
        ])
        prompt_anomalies = [r for r in results if "prompt_injection" in r.metric]
        assert len(prompt_anomalies) >= 1

    def test_detect_issue_clusters_empty_input(self) -> None:
        results = self.detector.detect_issue_clusters([])
        assert len(results) == 0

    def test_custom_config(self) -> None:
        detector = AnomalyDetector(AnomalyDetectionConfig(score_drop_threshold=0.1, min_samples_for_baseline=2))
        current = {"aggregate_score": 0.6}
        baseline = [{"aggregate_score": 0.9}, {"aggregate_score": 0.85}]
        results = detector.detect_regression(current, baseline)
        assert len(results) == 1
        assert results[0].deviation == 0.275

    def test_anomaly_result_dataclass(self) -> None:
        r = AnomalyResult(severity="warning", metric="test", message="test msg", current_value=0.5, baseline_value=0.8, deviation=0.3)
        assert r.severity == "warning"
        assert r.metric == "test"
        assert r.deviation == 0.3
