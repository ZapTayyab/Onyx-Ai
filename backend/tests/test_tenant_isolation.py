from __future__ import annotations

import uuid
import pytest
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.core.database import Base, get_async_session
from app.models.postgres import (
    Organization,
    TargetAgent,
    EvaluationSuite,
    RunMetadata,
    User,
)
from app.config import BillingPlan, UserRole, AgentType, RunStatus
from app.repositories.evaluations import SQLEvaluationRepository
from app.repositories.agents import SQLAgentRepository


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        json_serializer=lambda o: str(o) if not isinstance(o, (dict, list)) else __import__("json").dumps(o),
    )
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.exec_driver_sql("PRAGMA foreign_keys = ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def seeded_tenants(db_session: AsyncSession):
    # Tenant A
    org_a = Organization(name="Tenant A", slug="tenant-a", billing_plan=BillingPlan.PRO)
    db_session.add(org_a)
    await db_session.flush()

    user_a = User(
        organization_id=org_a.id,
        email="admin@tenant-a.com",
        auth_provider_id=f"dev:user-a-{uuid.uuid4()}",
        role=UserRole.ADMIN,
    )
    db_session.add(user_a)

    agent_a1 = TargetAgent(
        organization_id=org_a.id,
        name="Agent A1",
        agent_type=AgentType.OPENAI,
        model_name="gpt-4o",
    )
    agent_a2 = TargetAgent(
        organization_id=org_a.id,
        name="Agent A2",
        agent_type=AgentType.ANTHROPIC,
        model_name="claude-3-5-sonnet",
    )
    db_session.add_all([agent_a1, agent_a2])

    suite_a1 = EvaluationSuite(
        organization_id=org_a.id,
        name="Suite A1",
        persona_config=[{"name": "User A"}],
    )
    db_session.add(suite_a1)
    await db_session.flush()

    run_a1 = RunMetadata(
        organization_id=org_a.id,
        suite_id=suite_a1.id,
        agent_id=agent_a1.id,
        total_sessions=2,
    )
    db_session.add(run_a1)

    # Tenant B
    org_b = Organization(name="Tenant B", slug="tenant-b", billing_plan=BillingPlan.ENTERPRISE)
    db_session.add(org_b)
    await db_session.flush()

    user_b = User(
        organization_id=org_b.id,
        email="admin@tenant-b.com",
        auth_provider_id=f"dev:user-b-{uuid.uuid4()}",
        role=UserRole.ADMIN,
    )
    db_session.add(user_b)

    agent_b1 = TargetAgent(
        organization_id=org_b.id,
        name="Agent B1",
        agent_type=AgentType.CUSTOM,
        model_name="mock-model",
    )
    agent_b2 = TargetAgent(
        organization_id=org_b.id,
        name="Agent B2",
        agent_type=AgentType.OPENAI,
        model_name="gpt-4o-mini",
    )
    agent_b3 = TargetAgent(
        organization_id=org_b.id,
        name="Agent B3",
        agent_type=AgentType.VLLM,
        model_name="llama-3-70b",
    )
    db_session.add_all([agent_b1, agent_b2, agent_b3])

    suite_b1 = EvaluationSuite(
        organization_id=org_b.id,
        name="Suite B1",
        persona_config=[{"name": "User B1"}],
    )
    suite_b2 = EvaluationSuite(
        organization_id=org_b.id,
        name="Suite B2",
        persona_config=[{"name": "User B2"}],
    )
    db_session.add_all([suite_b1, suite_b2])
    await db_session.flush()

    run_b1 = RunMetadata(
        organization_id=org_b.id,
        suite_id=suite_b1.id,
        agent_id=agent_b1.id,
        total_sessions=5,
    )
    run_b2 = RunMetadata(
        organization_id=org_b.id,
        suite_id=suite_b2.id,
        agent_id=agent_b2.id,
        total_sessions=10,
    )
    db_session.add_all([run_b1, run_b2])

    await db_session.commit()

    return {
        "org_a": org_a,
        "user_a": user_a,
        "agent_a1": agent_a1,
        "agent_a2": agent_a2,
        "suite_a1": suite_a1,
        "run_a1": run_a1,
        "org_b": org_b,
        "user_b": user_b,
        "agent_b1": agent_b1,
        "agent_b2": agent_b2,
        "agent_b3": agent_b3,
        "suite_b1": suite_b1,
        "suite_b2": suite_b2,
        "run_b1": run_b1,
        "run_b2": run_b2,
    }


class TestRepositoryBehavioralTenantIsolation:

    @pytest.mark.asyncio
    async def test_get_agent_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants
        repo = SQLAgentRepository(db_session)

        # Negative case: Org A requests Org B's agent -> returns None
        agent_b = await repo.get_agent(agent_id=data["agent_b1"].id, organization_id=data["org_a"].id)
        assert agent_b is None, "Org A must NOT be able to read Org B's agent"

        # Positive case: Org A requests own agent -> returns agent
        own_agent = await repo.get_agent(agent_id=data["agent_a1"].id, organization_id=data["org_a"].id)
        assert own_agent is not None
        assert own_agent.id == data["agent_a1"].id
        assert own_agent.name == "Agent A1"

    @pytest.mark.asyncio
    async def test_list_agents_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants
        repo = SQLAgentRepository(db_session)

        agents_a = await repo.list_agents(organization_id=data["org_a"].id)
        agent_a_ids = {a.id for a in agents_a}

        # Positive case: exact count and items belonging to Org A
        assert len(agents_a) == 2
        assert data["agent_a1"].id in agent_a_ids
        assert data["agent_a2"].id in agent_a_ids

        # Negative case: Zero Org B agents are returned
        assert data["agent_b1"].id not in agent_a_ids
        assert data["agent_b2"].id not in agent_a_ids
        assert data["agent_b3"].id not in agent_a_ids

    @pytest.mark.asyncio
    async def test_get_suite_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants
        repo = SQLEvaluationRepository(db_session)

        # Negative case: Org A requests Org B's suite -> returns None
        suite_b = await repo.get_suite(suite_id=data["suite_b1"].id, organization_id=data["org_a"].id)
        assert suite_b is None, "Org A must NOT be able to read Org B's suite"

        # Positive case: Org A requests own suite -> returns suite
        own_suite = await repo.get_suite(suite_id=data["suite_a1"].id, organization_id=data["org_a"].id)
        assert own_suite is not None
        assert own_suite.id == data["suite_a1"].id
        assert own_suite.name == "Suite A1"

    @pytest.mark.asyncio
    async def test_get_run_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants
        repo = SQLEvaluationRepository(db_session)

        # Negative case: Org A requests Org B's run -> returns None
        run_b = await repo.get_run(run_id=data["run_b1"].id, organization_id=data["org_a"].id)
        assert run_b is None, "Org A must NOT be able to read Org B's run"

        # Positive case: Org A requests own run -> returns run
        own_run = await repo.get_run(run_id=data["run_a1"].id, organization_id=data["org_a"].id)
        assert own_run is not None
        assert own_run.id == data["run_a1"].id
        assert own_run.total_sessions == 2

    @pytest.mark.asyncio
    async def test_list_runs_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants
        repo = SQLEvaluationRepository(db_session)

        runs_a = await repo.list_runs(organization_id=data["org_a"].id, page=1, per_page=100)
        run_a_ids = {r.id for r in runs_a}

        # Positive case: exact count and items belonging to Org A
        assert len(runs_a) == 1
        assert data["run_a1"].id in run_a_ids

        # Negative case: zero Org B runs are returned (even though Org B has 2 runs vs Org A's 1 run)
        assert data["run_b1"].id not in run_a_ids
        assert data["run_b2"].id not in run_a_ids


class TestRouterBehavioralTenantIsolation:

    def _make_token(self, user_auth_id: str, org_id: uuid.UUID, role: str = "admin") -> str:
        secret = "dev-secret-key-change-in-production"
        return jwt.encode(
            {
                "sub": user_auth_id,
                "org_id": str(org_id),
                "role": role,
                "email": "user@example.com",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            secret,
            algorithm="HS256",
        )

    @pytest.mark.asyncio
    async def test_router_get_agent_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants

        async def override_get_db():
            yield db_session

        class MockSessionFactory:
            def __call__(self):
                class AsyncCtx:
                    async def __aenter__(ctx_self):
                        return db_session
                    async def __aexit__(ctx_self, exc_type, exc_val, exc_tb):
                        pass
                return AsyncCtx()

        with (
            patch("app.core.database.init_db", new_callable=AsyncMock),
            patch("app.core.database.close_db", new_callable=AsyncMock),
            patch("app.core.cache.cache_service.initialize", new_callable=AsyncMock),
            patch("app.core.cache.cache_service.close", new_callable=AsyncMock),
            patch("app.core.clickhouse.clickhouse_mgr.connect"),
            patch("app.core.clickhouse.clickhouse_mgr.execute", new_callable=AsyncMock, return_value=[]),
            patch("app.core.clickhouse.clickhouse_mgr.close"),
            patch("app.core.clickhouse.clickhouse_mgr.health_check", return_value=True),
            patch("app.core.database._get_session_factory", return_value=MockSessionFactory()),
        ):
            from app.main import app
            app.dependency_overrides[get_async_session] = override_get_db
            with TestClient(app, raise_server_exceptions=False) as client:
                token_a = self._make_token(
                    user_auth_id=data["user_a"].auth_provider_id,
                    org_id=data["org_a"].id,
                )
                # Negative case: User from Org A requests Org B's agent ID -> 404
                res_b = client.get(
                    f"/v1/agents/{data['agent_b1'].id}",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert res_b.status_code == 404, f"Expected 404 Not Found, got {res_b.status_code}: {res_b.text}"

                # Positive case: User from Org A requests own agent ID -> 200 OK
                res_a = client.get(
                    f"/v1/agents/{data['agent_a1'].id}",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert res_a.status_code == 200, f"Expected 200 OK, got {res_a.status_code}: {res_a.text}"
                assert res_a.json()["id"] == str(data["agent_a1"].id)

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_router_get_suite_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants

        async def override_get_db():
            yield db_session

        class MockSessionFactory:
            def __call__(self):
                class AsyncCtx:
                    async def __aenter__(ctx_self):
                        return db_session
                    async def __aexit__(ctx_self, exc_type, exc_val, exc_tb):
                        pass
                return AsyncCtx()

        with (
            patch("app.core.database.init_db", new_callable=AsyncMock),
            patch("app.core.database.close_db", new_callable=AsyncMock),
            patch("app.core.cache.cache_service.initialize", new_callable=AsyncMock),
            patch("app.core.cache.cache_service.close", new_callable=AsyncMock),
            patch("app.core.clickhouse.clickhouse_mgr.connect"),
            patch("app.core.clickhouse.clickhouse_mgr.execute", new_callable=AsyncMock, return_value=[]),
            patch("app.core.clickhouse.clickhouse_mgr.close"),
            patch("app.core.clickhouse.clickhouse_mgr.health_check", return_value=True),
            patch("app.core.database._get_session_factory", return_value=MockSessionFactory()),
        ):
            from app.main import app
            app.dependency_overrides[get_async_session] = override_get_db
            with TestClient(app, raise_server_exceptions=False) as client:
                token_a = self._make_token(
                    user_auth_id=data["user_a"].auth_provider_id,
                    org_id=data["org_a"].id,
                )
                # Negative case: User from Org A requests Org B's suite ID -> 404
                res_b = client.get(
                    f"/v1/suites/{data['suite_b1'].id}",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert res_b.status_code == 404, f"Expected 404 Not Found, got {res_b.status_code}: {res_b.text}"

                # Positive case: User from Org A requests own suite ID -> 200 OK
                res_a = client.get(
                    f"/v1/suites/{data['suite_a1'].id}",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert res_a.status_code == 200, f"Expected 200 OK, got {res_a.status_code}: {res_a.text}"
                assert res_a.json()["id"] == str(data["suite_a1"].id)

            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_router_get_run_status_cross_tenant(self, db_session: AsyncSession, seeded_tenants: dict):
        data = seeded_tenants

        async def override_get_db():
            yield db_session

        class MockSessionFactory:
            def __call__(self):
                class AsyncCtx:
                    async def __aenter__(ctx_self):
                        return db_session
                    async def __aexit__(ctx_self, exc_type, exc_val, exc_tb):
                        pass
                return AsyncCtx()

        with (
            patch("app.core.database.init_db", new_callable=AsyncMock),
            patch("app.core.database.close_db", new_callable=AsyncMock),
            patch("app.core.cache.cache_service.initialize", new_callable=AsyncMock),
            patch("app.core.cache.cache_service.close", new_callable=AsyncMock),
            patch("app.core.clickhouse.clickhouse_mgr.connect"),
            patch("app.core.clickhouse.clickhouse_mgr.execute", new_callable=AsyncMock, return_value=[]),
            patch("app.core.clickhouse.clickhouse_mgr.close"),
            patch("app.core.clickhouse.clickhouse_mgr.health_check", return_value=True),
            patch("app.core.database._get_session_factory", return_value=MockSessionFactory()),
        ):
            from app.main import app
            app.dependency_overrides[get_async_session] = override_get_db
            with TestClient(app, raise_server_exceptions=False) as client:
                token_a = self._make_token(
                    user_auth_id=data["user_a"].auth_provider_id,
                    org_id=data["org_a"].id,
                )
                # Negative case: User from Org A requests Org B's run ID -> 404
                res_b = client.get(
                    f"/v1/evaluations/runs/{data['run_b1'].id}",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert res_b.status_code == 404, f"Expected 404 Not Found, got {res_b.status_code}: {res_b.text}"

                # Positive case: User from Org A requests own run ID -> 200 OK
                res_a = client.get(
                    f"/v1/evaluations/runs/{data['run_a1'].id}",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert res_a.status_code == 200, f"Expected 200 OK, got {res_a.status_code}: {res_a.text}"
                assert res_a.json()["id"] == str(data["run_a1"].id)

            app.dependency_overrides.clear()
