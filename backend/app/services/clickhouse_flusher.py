from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.core.clickhouse import clickhouse_mgr
from app.models.clickhouse.traces import INSERT_TURN_TRACE
from app.models.postgres.run_metadata import RunMetadata
from app.services.llm_judge import SessionVerdict, TurnVerdict

logger = logging.getLogger("snt_ai.services.clickhouse_flusher")


class ClickHouseFlusher:
    BATCH_SIZE = 100

    async def flush_turn_traces(
        self,
        organization_id: str,
        run_id: str,
        session_id: str,
        persona_name: str,
        turns: list[dict[str, Any]],
        turn_verdicts: list[TurnVerdict],
        chaos_log: list[dict[str, Any]],
        model_name: str,
    ) -> int:
        rows: list[dict[str, Any]] = []

        for turn_data, verdict in zip(turns, turn_verdicts):
            timestamp = turn_data.get("timestamp", datetime.now(timezone.utc))
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()

            for speaker in ["user", "agent"]:
                rows.append({
                    "organization_id": organization_id,
                    "session_id": session_id,
                    "run_id": run_id,
                    "turn_id": verdict.turn_index,
                    "timestamp": timestamp,
                    "speaker": speaker,
                    "turn_text": turn_data.get(speaker, ""),
                    "token_count": turn_data.get("token_count_" + speaker, 0),
                    "latency_ms": turn_data.get("latency_ms", 0.0),
                    "model_name": model_name,
                    "chaos_injected": json.dumps(chaos_log[verdict.turn_index] if verdict.turn_index < len(chaos_log) else {}),
                    "scores": json.dumps({
                        "groundedness": verdict.rubric_scores.groundedness,
                        "compliance": verdict.rubric_scores.compliance,
                        "robustness": verdict.rubric_scores.robustness,
                        "overall": verdict.score,
                    }),
                    "metadata": json.dumps({
                        "persona_name": persona_name,
                        "speaker": speaker,
                        "passed": verdict.passed,
                        "reason": verdict.reason,
                    }),
                })

        if rows:
            for i in range(0, len(rows), self.BATCH_SIZE):
                batch = rows[i : i + self.BATCH_SIZE]
                try:
                    await clickhouse_mgr.execute_batch(INSERT_TURN_TRACE, batch)
                except Exception as exc:
                    logger.error("Failed to flush %d trace rows: %s", len(batch), exc)
                    raise

            logger.info("Flushed %d trace rows for session %s", len(rows), session_id)

        return len(rows)

    async def update_run_metadata(
        self,
        db_session: Any,
        run: RunMetadata,
        session_verdicts: list[SessionVerdict],
    ) -> None:
        passed = sum(1 for sv in session_verdicts if sv.aggregate_score >= 70.0)
        total = len(session_verdicts)
        avg_score = round(sum(sv.aggregate_score for sv in session_verdicts) / total, 2) if total else 0.0

        avg_groundedness = round(
            sum(sv.rubric_averages.groundedness for sv in session_verdicts) / total, 4
        ) if total else 0.0
        avg_compliance = round(
            sum(sv.rubric_averages.compliance for sv in session_verdicts) / total, 4
        ) if total else 0.0
        avg_robustness = round(
            sum(sv.rubric_averages.robustness for sv in session_verdicts) / total, 4
        ) if total else 0.0

        run.completed_sessions = total
        run.aggregate_score = avg_score
        run.summary_metrics = {
            "passed_sessions": passed,
            "total_sessions": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
            "avg_groundedness": avg_groundedness,
            "avg_compliance": avg_compliance,
            "avg_robustness": avg_robustness,
            "total_turns_evaluated": sum(sv.total_turns for sv in session_verdicts),
        }
        run.completed_at = datetime.now(timezone.utc)

        logger.info(
            "Run %s complete: score=%.2f passed=%d/%d",
            run.id, avg_score, passed, total,
        )
