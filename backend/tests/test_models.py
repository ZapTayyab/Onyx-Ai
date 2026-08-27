from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.postgres import (
    EvaluationSuite,
    Organization,
    RunMetadata,
    TargetAgent,
    User,
)
from app.config import BillingPlan, UserRole, AgentType, RunStatus


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


async def _seed_org(db: AsyncSession) -> Organization:
    org = Organization(
        name="Test Org",
        slug="test-org",
        billing_plan=BillingPlan.PRO,
    )
    db.add(org)
    await db.flush()
    await db.refresh(org)
    return org


async def _seed_user(db: AsyncSession, org_id: uuid.UUID) -> User:
    user = User(
        organization_id=org_id,
        email="test@example.com",
        auth_provider_id="auth0|12345",
        role=UserRole.ADMIN,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def _seed_agent(db: AsyncSession, org_id: uuid.UUID) -> TargetAgent:
    agent = TargetAgent(
        organization_id=org_id,
        name="Test Agent",
        agent_type=AgentType.OPENAI,
        model_name="gpt-4o",
        system_prompt="You are a helpful assistant.",
        config={"temperature": 0.7},
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return agent


async def _seed_suite(db: AsyncSession, org_id: uuid.UUID) -> EvaluationSuite:
    suite = EvaluationSuite(
        organization_id=org_id,
        name="Test Suite",
        persona_config=[
            {"name": "Standard User", "category": "standard"},
            {"name": "Adversarial User", "category": "adversarial"},
        ],
        chaos_profiles={"network_latency": {"enabled": True}},
        judge_config={"provider": "openai", "model": "gpt-4o"},
    )
    db.add(suite)
    await db.flush()
    await db.refresh(suite)
    return suite


class TestOrganizationModel:
    async def test_create_organization(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        assert org.id is not None
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert org.billing_plan == BillingPlan.PRO
        assert org.is_active is True
        assert org.created_at is not None
        assert org.updated_at is not None

    async def test_organization_slug_unique(self, db_session: AsyncSession) -> None:
        await _seed_org(db_session)
        dup = Organization(name="Dup Org", slug="test-org", billing_plan=BillingPlan.FREE)
        db_session.add(dup)
        with pytest.raises(Exception):
            await db_session.flush()


class TestUserModel:
    async def test_create_user(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        user = await _seed_user(db_session, org.id)
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN
        assert user.organization_id == org.id
        assert user.is_active is True

    async def test_user_org_relationship(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        user = await _seed_user(db_session, org.id)
        loaded_org = user.organization
        assert loaded_org is not None
        assert loaded_org.id == org.id


class TestTargetAgentModel:
    async def test_create_agent(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        agent = await _seed_agent(db_session, org.id)
        assert agent.id is not None
        assert agent.name == "Test Agent"
        assert agent.agent_type == AgentType.OPENAI
        assert agent.model_name == "gpt-4o"

    async def test_agent_org_relationship(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        agent = await _seed_agent(db_session, org.id)
        assert agent.organization.id == org.id


class TestEvaluationSuiteModel:
    async def test_create_suite(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        suite = await _seed_suite(db_session, org.id)
        assert suite.id is not None
        assert suite.name == "Test Suite"
        assert len(suite.persona_config) == 2
        assert "network_latency" in suite.chaos_profiles

    async def test_suite_with_defaults(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        suite = EvaluationSuite(
            organization_id=org.id,
            name="Minimal Suite",
        )
        db_session.add(suite)
        await db_session.flush()
        await db_session.refresh(suite)
        assert suite.persona_config == []
        assert suite.chaos_profiles == {}
        assert suite.judge_config == {}
        assert suite.is_active is True


class TestRunMetadataModel:
    async def test_create_run(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        agent = await _seed_agent(db_session, org.id)
        suite = await _seed_suite(db_session, org.id)

        run = RunMetadata(
            organization_id=org.id,
            suite_id=suite.id,
            agent_id=agent.id,
            total_sessions=5,
        )
        db_session.add(run)
        await db_session.flush()
        await db_session.refresh(run)

        assert run.id is not None
        assert run.status == RunStatus.PENDING
        assert run.total_sessions == 5
        assert run.completed_sessions == 0

    async def test_run_status_transition(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        agent = await _seed_agent(db_session, org.id)
        suite = await _seed_suite(db_session, org.id)

        run = RunMetadata(
            organization_id=org.id,
            suite_id=suite.id,
            agent_id=agent.id,
            total_sessions=3,
            status=RunStatus.RUNNING,
        )
        db_session.add(run)
        await db_session.flush()
        assert run.status == RunStatus.RUNNING

        run.status = RunStatus.COMPLETED
        run.aggregate_score = 87.5
        await db_session.flush()
        assert run.status == RunStatus.COMPLETED
        assert run.aggregate_score == 87.5


class TestModelRelationships:
    async def test_org_has_users(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        await _seed_user(db_session, org.id)
        user2 = User(
            organization_id=org.id,
            email="user2@example.com",
            auth_provider_id="auth0|67890",
        )
        db_session.add(user2)
        await db_session.flush()
        await db_session.refresh(org)

        assert len(org.users) >= 2

    async def test_org_has_agents_and_suites(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        await _seed_agent(db_session, org.id)
        await _seed_suite(db_session, org.id)
        await db_session.refresh(org)

        assert len(org.target_agents) == 1
        assert len(org.evaluation_suites) == 1

    async def test_org_delete_cascades_to_users(self, db_session: AsyncSession) -> None:
        org = await _seed_org(db_session)
        await _seed_user(db_session, org.id)
        org_id = org.id

        await db_session.delete(org)
        await db_session.flush()

        remaining_users = (await db_session.execute(select(User).where(User.organization_id == org_id))).scalars().all()
        remaining_orgs = (await db_session.execute(select(Organization).where(Organization.id == org_id))).scalars().all()
        assert len(remaining_users) == 0
        assert len(remaining_orgs) == 0
