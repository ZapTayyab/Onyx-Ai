from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from collections import defaultdict

logger = logging.getLogger("snt_ai.services.alerting")


class AlertingService:
    def __init__(self) -> None:
        self._webhooks: dict[str, list[str]] = defaultdict(list)

    def register_webhook(self, organization_id: str, url: str) -> None:
        if url not in self._webhooks[organization_id]:
            self._webhooks[organization_id].append(url)
            logger.info("Webhook registered for org %s: %s", organization_id, url)

    def unregister_webhook(self, organization_id: str, url: str) -> None:
        if url in self._webhooks.get(organization_id, []):
            self._webhooks[organization_id].remove(url)
            logger.info("Webhook unregistered for org %s: %s", organization_id, url)

    async def send_alert(
        self,
        organization_id: str,
        alert_type: str,
        severity: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        logger.info(
            "Alert for org %s: [%s/%s] %s",
            organization_id, severity, alert_type, message,
        )

        urls = self._webhooks.get(organization_id, [])
        for url in urls:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    logger.debug("Alert delivered to %s: %s", url, resp.status_code)
            except Exception as exc:
                logger.warning("Failed to deliver alert to %s: %s", url, exc)

    async def send_score_regression_alert(
        self,
        organization_id: str,
        run_id: str,
        current_score: float,
        baseline_score: float,
        details: list[str] | None = None,
    ) -> None:
        drop = baseline_score - current_score
        severity = "critical" if drop > 0.25 else "warning"
        message = (
            f"Score regression detected in run {run_id[:8]}: "
            f"{baseline_score:.2%} -> {current_score:.2%} (drop of {drop:.2%})"
        )
        await self.send_alert(
            organization_id=organization_id,
            alert_type="score_regression",
            severity=severity,
            message=message,
            metadata={
                "run_id": run_id,
                "current_score": current_score,
                "baseline_score": baseline_score,
                "drop": drop,
                "details": details or [],
            },
        )

    async def send_evaluation_completed_alert(
        self,
        organization_id: str,
        run_id: str,
        suite_name: str,
        aggregate_score: float,
        total_sessions: int,
        failed_sessions: int,
    ) -> None:
        severity = "warning" if aggregate_score < 0.6 else "info"
        message = (
            f"Evaluation '{suite_name}' completed: "
            f"score={aggregate_score:.2%}, "
            f"{failed_sessions}/{total_sessions} sessions failed"
        )
        await self.send_alert(
            organization_id=organization_id,
            alert_type="evaluation_completed",
            severity=severity,
            message=message,
            metadata={
                "run_id": run_id,
                "suite_name": suite_name,
                "aggregate_score": aggregate_score,
                "total_sessions": total_sessions,
                "failed_sessions": failed_sessions,
            },
        )


alerting_service = AlertingService()
