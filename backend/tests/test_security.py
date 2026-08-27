from __future__ import annotations

from app.core.security import _map_clerk_role, _map_auth0_role, create_audit_log
from app.config import UserRole


class TestRoleMapping:
    def test_map_clerk_admin(self) -> None:
        assert _map_clerk_role("org:admin") == UserRole.ADMIN

    def test_map_clerk_member(self) -> None:
        assert _map_clerk_role("org:member") == UserRole.MEMBER

    def test_map_clerk_viewer(self) -> None:
        assert _map_clerk_role("org:viewer") == UserRole.VIEWER

    def test_map_clerk_unknown_role_defaults_viewer(self) -> None:
        assert _map_clerk_role("org:unknown") == UserRole.VIEWER

    def test_map_auth0_admin(self) -> None:
        assert _map_auth0_role(["admin", "member"]) == UserRole.ADMIN

    def test_map_auth0_member(self) -> None:
        assert _map_auth0_role(["member"]) == UserRole.MEMBER

    def test_map_auth0_viewer(self) -> None:
        assert _map_auth0_role(["viewer"]) == UserRole.VIEWER

    def test_map_auth0_empty_roles(self) -> None:
        assert _map_auth0_role([]) == UserRole.VIEWER


class TestAuditLog:
    def test_create_audit_log(self) -> None:
        log = create_audit_log(
            user_id="user_123",
            org_id="org_456",
            action="run_evaluation",
            resource="/v1/evaluations/run",
            success=True,
        )
        assert log.user_id == "user_123"
        assert log.org_id == "org_456"
        assert log.action == "run_evaluation"
        assert log.success is True
        assert log.timestamp is not None
        assert log.timestamp.endswith("Z") or "+" in log.timestamp

    def test_audit_log_with_metadata(self) -> None:
        log = create_audit_log(
            user_id="user_789",
            org_id="org_012",
            action="delete_agent",
            resource="/v1/agents/abc-123",
            success=False,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        assert log.ip_address == "192.168.1.1"
        assert log.user_agent == "Mozilla/5.0"
