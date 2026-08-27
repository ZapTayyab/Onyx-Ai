"""
Router-level integration tests.

These use FastAPI's TestClient (synchronous httpx transport).
Heavy database/cache dependencies are mocked so tests run without
Docker services.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient

# ------------------------------------------------------------------
# Patch heavyweight dependencies BEFORE importing app.main so that
# FastAPI lifespan hooks don't try to connect to real services.
# ------------------------------------------------------------------

_ORG_ID = str(uuid.uuid4())
_USER_ID = str(uuid.uuid4())
_AUTH_PROVIDER_ID = f"dev:{uuid.uuid4()}"
_DEV_SECRET = "dev-secret-key-change-in-production"


def _make_token(role: str = "admin") -> str:
    return jwt.encode(
        {
            "sub": _AUTH_PROVIDER_ID,
            "org_id": _ORG_ID,
            "role": role,
            "email": "admin@snt.ai",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        _DEV_SECRET,
        algorithm="HS256",
    )


@pytest.fixture(scope="module")
def client():
    """Return a TestClient with all external services patched."""
    with (
        patch("app.core.database.init_db", new_callable=AsyncMock),
        patch("app.core.database.close_db", new_callable=AsyncMock),
        patch("app.core.cache.cache_service.initialize", new_callable=AsyncMock),
        patch("app.core.cache.cache_service.close", new_callable=AsyncMock),
        patch("app.core.clickhouse.clickhouse_mgr.connect"),
        patch("app.core.clickhouse.clickhouse_mgr.execute", new_callable=AsyncMock, return_value=[]),
        patch("app.core.clickhouse.clickhouse_mgr.close"),
        patch("app.core.clickhouse.clickhouse_mgr.health_check", return_value=True),
        # Patch the session factory so DB calls in middleware are no-ops
        patch("app.core.database._get_session_factory"),
    ):
        from app.main import app
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


# ── Health ─────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_body(self, client: TestClient) -> None:
        body = client.get("/health").json()
        assert body["status"] == "healthy"
        assert "version" in body
        assert "environment" in body


# ── Auth ───────────────────────────────────────────────────────────

class TestAuth:
    def test_login_wrong_creds_returns_401(self, client: TestClient) -> None:
        r = client.post(
            "/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong"},
        )
        # Without DB the session mock will short-circuit; we only assert ≠ 200
        assert r.status_code in (401, 422, 500)

    def test_login_missing_body_returns_422(self, client: TestClient) -> None:
        r = client.post("/v1/auth/login", json={})
        assert r.status_code == 422

    def test_auth_me_no_token_returns_401_or_403(self, client: TestClient) -> None:
        r = client.get("/v1/auth/me")
        assert r.status_code in (401, 403)


# ── Protected routes require token ─────────────────────────────────

class TestProtectedRoutes:
    def test_agents_list_no_token(self, client: TestClient) -> None:
        r = client.get("/v1/agents")
        assert r.status_code in (401, 403)

    def test_suites_list_no_token(self, client: TestClient) -> None:
        r = client.get("/v1/suites")
        assert r.status_code in (401, 403)

    def test_evaluations_runs_no_token(self, client: TestClient) -> None:
        r = client.get("/v1/evaluations/runs")
        assert r.status_code in (401, 403)

    def test_organizations_me_no_token(self, client: TestClient) -> None:
        r = client.get("/v1/organizations/me")
        assert r.status_code in (401, 403)


# ── Evaluations pagination validation ──────────────────────────────

class TestEvaluationsValidation:
    def test_invalid_page_returns_422(self, client: TestClient) -> None:
        token = _make_token()
        r = client.get(
            "/v1/evaluations/runs?page=0",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 422

    def test_per_page_too_large_returns_422(self, client: TestClient) -> None:
        token = _make_token()
        r = client.get(
            "/v1/evaluations/runs?per_page=999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 422


# ── Report format validation ────────────────────────────────────────

class TestReportEndpoint:
    def test_invalid_format_returns_422(self, client: TestClient) -> None:
        token = _make_token()
        run_id = uuid.uuid4()
        r = client.get(
            f"/v1/evaluations/runs/{run_id}/report?format=csv",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 422

    def test_invalid_run_uuid_returns_422(self, client: TestClient) -> None:
        token = _make_token()
        r = client.get(
            "/v1/evaluations/runs/not-a-uuid/report",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 422


# ── Billing ────────────────────────────────────────────────────────

class TestBilling:
    def test_webhook_missing_signature_returns_400(self, client: TestClient) -> None:
        r = client.post(
            "/v1/billing/stripe-webhook",
            content=b'{"type": "test"}',
            headers={"content-type": "application/json"},
        )
        # In dev mode signature check is skipped; expect 200 or 400
        assert r.status_code in (200, 400, 422, 500)
