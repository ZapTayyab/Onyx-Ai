from __future__ import annotations

import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("snt_ai.services.anomaly_detector")


@dataclass
class AnomalyResult:
    severity: str  # "info", "warning", "critical"
    metric: str
    message: str
    current_value: float
    baseline_value: float
    deviation: float


@dataclass
class AnomalyDetectionConfig:
    score_drop_threshold: float = 0.15
    latency_increase_threshold: float = 0.50
    failure_rate_threshold: float = 0.30
    min_samples_for_baseline: int = 3
    z_score_threshold: float = 2.0


class AnomalyDetector:
    def __init__(self, config: AnomalyDetectionConfig | None = None) -> None:
        self.config = config or AnomalyDetectionConfig()

    def detect_regression(
        self,
        current_run: dict[str, Any],
        baseline_runs: list[dict[str, Any]],
    ) -> list[AnomalyResult]:
        anomalies: list[AnomalyResult] = []
        current_score = current_run.get("aggregate_score", 0.0)

        if len(baseline_runs) < self.config.min_samples_for_baseline:
            return anomalies

        historical_scores = [
            r.get("aggregate_score", 0.0)
            for r in baseline_runs
            if r.get("aggregate_score") is not None
        ]
        if not historical_scores:
            return anomalies

        baseline_avg = statistics.mean(historical_scores)
        baseline_stdev = statistics.stdev(historical_scores) if len(historical_scores) > 1 else 0.05
        score_drop = baseline_avg - current_score

        if score_drop > self.config.score_drop_threshold:
            z_score = score_drop / max(baseline_stdev, 0.01)
            severity = "critical" if z_score > 3.0 else ("warning" if z_score > 2.0 else "info")
            anomalies.append(AnomalyResult(
                severity=severity,
                metric="aggregate_score",
                message=f"Aggregate score dropped from {baseline_avg:.2%} to {current_score:.2%} (drop: {score_drop:.2%}, z={z_score:.1f})",
                current_value=current_score,
                baseline_value=baseline_avg,
                deviation=score_drop,
            ))

        current_latency = current_run.get("avg_latency_ms", 0.0)
        historical_latencies = [
            r.get("avg_latency_ms", 0.0)
            for r in baseline_runs
            if r.get("avg_latency_ms") is not None
        ]
        if historical_latencies and current_latency > 0:
            latency_baseline = statistics.mean(historical_latencies)
            if latency_baseline > 0:
                latency_increase = (current_latency - latency_baseline) / latency_baseline
                if latency_increase > self.config.latency_increase_threshold:
                    anomalies.append(AnomalyResult(
                        severity="warning" if latency_increase > 0.8 else "info",
                        metric="latency_ms",
                        message=f"Average latency increased by {latency_increase:.1%} ({latency_baseline:.0f}ms -> {current_latency:.0f}ms)",
                        current_value=current_latency,
                        baseline_value=latency_baseline,
                        deviation=latency_increase,
                    ))

        return anomalies

    def detect_persona_anomalies(
        self,
        session_verdicts: list[dict[str, Any]],
    ) -> list[AnomalyResult]:
        anomalies: list[AnomalyResult] = []
        category_scores: dict[str, list[float]] = defaultdict(list)
        category_map: dict[str, str] = {
            "HelpSeeker": "standard", "PowerUser": "standard", "NewComer": "standard",
            "ConfusedUser": "edge_case", "RapidTyper": "edge_case", "NonEnglish": "edge_case",
            "Jailbreaker": "adversarial", "DataMiner": "adversarial", "RolePlayer": "adversarial",
        }

        for sv in session_verdicts:
            pname = sv.get("persona_name", "")
            cat = category_map.get(pname, "standard")
            category_scores[cat].append(sv.get("aggregate_score", 0.0))

        for category, scores in category_scores.items():
            if not scores:
                continue
            avg = statistics.mean(scores)
            threshold_map = {"standard": 0.7, "edge_case": 0.5, "adversarial": 0.4}
            threshold = threshold_map.get(category, 0.5)
            if avg < threshold:
                anomalies.append(AnomalyResult(
                    severity="warning" if avg < threshold * 0.8 else "info",
                    metric=f"{category}_score",
                    message=f"Category '{category}' average score {avg:.2%} is below threshold {threshold:.0%}",
                    current_value=avg,
                    baseline_value=threshold,
                    deviation=threshold - avg,
                ))

        return anomalies

    def detect_issue_clusters(
        self,
        turn_verdicts_per_session: list[list[dict[str, Any]]],
    ) -> list[AnomalyResult]:
        anomalies: list[AnomalyResult] = []
        issue_counts: dict[str, int] = defaultdict(int)
        total_turns = 0

        for session_turns in turn_verdicts_per_session:
            for tv in session_turns:
                total_turns += 1
                for issue in tv.get("detected_issues", []):
                    issue_counts[issue] += 1

        if total_turns == 0:
            return anomalies

        for issue, count in issue_counts.items():
            rate = count / total_turns
            if rate > 0.3:
                anomalies.append(AnomalyResult(
                    severity="warning" if rate > 0.5 else "info",
                    metric=f"issue_{issue}",
                    message=f"Issue '{issue}' appears in {rate:.0%} of turns ({count}/{total_turns})",
                    current_value=rate,
                    baseline_value=0.0,
                    deviation=rate,
                ))

        return anomalies
