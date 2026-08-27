"""Application services for audit execution, summaries, and persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from config import AppConfig, get_config
from logging_config import get_logger
from stress_test_engine import generate_report_string, run_stress_test_sessions


logger = get_logger(__name__)


@dataclass(frozen=True)
class AuditSummary:
    """Aggregate dashboard-friendly metrics."""

    score: float
    total_sessions: int
    flagged_sessions: int
    total_turns: int
    failed_turns: int


class AuditService:
    """Coordinates corpus loading, execution, and report generation."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()

    def load_corpus(self, path: Path | None = None) -> list[dict]:
        corpus_path = path or self.config.corpus_path
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

        with corpus_path.open(encoding="utf-8") as handle:
            data = json.load(handle)

        if not isinstance(data, list) or not data:
            raise ValueError("Corpus must be a non-empty list of sessions.")

        logger.info("Loaded %s sessions from corpus", len(data))
        return data

    def run_audit(
        self,
        failure_rate: float,
        seed: int,
        corpus_path: Path | None = None,
    ) -> tuple[list[dict], str, AuditSummary]:
        corpus = self.load_corpus(corpus_path)
        results = run_stress_test_sessions(
            corpus=corpus,
            seed=seed,
            failure_rate=failure_rate,
        )
        report_text = generate_report_string(
            results,
            seed=seed,
            failure_rate=failure_rate,
            corpus_label=str(corpus_path or self.config.corpus_path),
        )
        summary = self.summarize(results)
        self.persist_report(report_text)
        logger.info(
            "Audit completed | sessions=%s turns=%s score=%.1f",
            summary.total_sessions,
            summary.total_turns,
            summary.score,
        )
        return results, report_text, summary

    def persist_report(self, report_text: str, path: Path | None = None) -> None:
        report_path = path or self.config.report_output_path
        report_path.write_text(report_text, encoding="utf-8")
        logger.info("Saved audit report to %s", report_path)

    @staticmethod
    def summarize(results: list[dict]) -> AuditSummary:
        total_turns = sum(len(item["turn_results"]) for item in results)
        failed_turns = sum(
            1 for item in results for turn in item["turn_results"] if not turn["passed"]
        )
        total_sessions = len(results)
        flagged_sessions = sum(1 for item in results if item["session_failed"])
        passed_turns = total_turns - failed_turns
        score = round((passed_turns / max(total_turns, 1)) * 100, 1)
        return AuditSummary(
            score=score,
            total_sessions=total_sessions,
            flagged_sessions=flagged_sessions,
            total_turns=total_turns,
            failed_turns=failed_turns,
        )
