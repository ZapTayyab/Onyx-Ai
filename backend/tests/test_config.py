from __future__ import annotations

from app.config import AppConfig, BillingPlan, RuntimeEnvironment, RunStatus, UserRole, AgentType


class TestAppConfig:
    def test_default_config_values(self) -> None:
        config = AppConfig()
        assert config.app_name == "SNT AI Assurance Platform"
        assert config.company_name == "SNT AI"
        assert config.environment == RuntimeEnvironment.DEVELOPMENT
        assert config.default_seed == 42
        assert config.default_failure_rate == 0.30

    def test_is_development_property(self) -> None:
        dev_config = AppConfig(environment=RuntimeEnvironment.DEVELOPMENT)
        assert dev_config.is_development is True
        assert dev_config.is_production is False

        prod_config = AppConfig(environment=RuntimeEnvironment.PRODUCTION)
        assert prod_config.is_development is False
        assert prod_config.is_production is True

    def test_parse_cors_origins(self) -> None:
        config = AppConfig(cors_origins=["http://localhost:3000"])
        assert "http://localhost:3000" in config.cors_origins

    def test_cors_origins_from_comma_separated_env(self, monkeypatch) -> None:
        # Regression: SNT_CORS_ORIGINS is a plain comma-separated string in
        # docker-compose — pydantic-settings must not require JSON for list fields.
        monkeypatch.setenv("SNT_CORS_ORIGINS", "https://app.example.com,http://localhost:3000")
        config = AppConfig(_env_file=None)
        assert config.cors_origins == ["https://app.example.com", "http://localhost:3000"]


class TestEnums:
    def test_billing_plan_values(self) -> None:
        assert BillingPlan.FREE.value == "free"
        assert BillingPlan.PRO.value == "pro"
        assert BillingPlan.ENTERPRISE.value == "enterprise"

    def test_user_role_values(self) -> None:
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MEMBER.value == "member"
        assert UserRole.VIEWER.value == "viewer"

    def test_agent_type_values(self) -> None:
        assert AgentType.OPENAI.value == "openai"
        assert AgentType.ANTHROPIC.value == "anthropic"
        assert AgentType.VLLM.value == "vllm"
        assert AgentType.CUSTOM.value == "custom"

    def test_run_status_transitions(self) -> None:
        assert RunStatus.PENDING.value == "pending"
        assert RunStatus.RUNNING.value == "running"
        assert RunStatus.COMPLETED.value == "completed"
        assert RunStatus.FAILED.value == "failed"
        assert RunStatus.CANCELLED.value == "cancelled"
