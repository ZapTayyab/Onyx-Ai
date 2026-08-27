from __future__ import annotations

from app.services.alerting import AlertingService


class TestAlertingService:
    def setup_method(self) -> None:
        self.service = AlertingService()
        self._org_id = "org-test-001"

    def test_register_webhook(self) -> None:
        self.service.register_webhook(self._org_id, "https://hooks.example.com/alerts")
        assert len(self.service._webhooks[self._org_id]) == 1

    def test_register_duplicate_webhook(self) -> None:
        url = "https://hooks.example.com/alerts"
        self.service.register_webhook(self._org_id, url)
        self.service.register_webhook(self._org_id, url)
        assert len(self.service._webhooks[self._org_id]) == 1

    def test_register_multiple_webhooks(self) -> None:
        self.service.register_webhook(self._org_id, "https://hooks.example.com/1")
        self.service.register_webhook(self._org_id, "https://hooks.example.com/2")
        assert len(self.service._webhooks[self._org_id]) == 2

    def test_unregister_webhook(self) -> None:
        url = "https://hooks.example.com/alerts"
        self.service.register_webhook(self._org_id, url)
        self.service.unregister_webhook(self._org_id, url)
        assert url not in self.service._webhooks.get(self._org_id, [])

    def test_unregister_nonexistent_webhook(self) -> None:
        self.service.unregister_webhook(self._org_id, "https://hooks.example.com/nonexistent")
        assert len(self.service._webhooks.get(self._org_id, [])) == 0

    async def test_send_alert_does_not_raise(self) -> None:
        await self.service.send_alert(
            organization_id=self._org_id,
            alert_type="test",
            severity="info",
            message="Test alert",
        )

    async def test_send_score_regression_alert_does_not_raise(self) -> None:
        await self.service.send_score_regression_alert(
            organization_id=self._org_id,
            run_id="run-001",
            current_score=0.6,
            baseline_score=0.9,
            details=["Score drop detected"],
        )

    async def test_send_evaluation_completed_alert_does_not_raise(self) -> None:
        await self.service.send_evaluation_completed_alert(
            organization_id=self._org_id,
            run_id="run-001",
            suite_name="Test Suite",
            aggregate_score=0.85,
            total_sessions=10,
            failed_sessions=2,
        )

    async def test_send_alert_with_metadata(self) -> None:
        await self.service.send_alert(
            organization_id=self._org_id,
            alert_type="custom",
            severity="critical",
            message="Custom alert with metadata",
            metadata={"key": "value", "count": 42},
        )
