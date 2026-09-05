from __future__ import annotations

import os
from enum import StrEnum
from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeEnvironment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class BillingPlan(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class AgentType(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    VLLM = "vllm"
    CUSTOM = "custom"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="SNT_",
    )

    environment: RuntimeEnvironment = RuntimeEnvironment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"
    app_name: str = "SNT AI Assurance Platform"
    company_name: str = "SNT AI"
    support_email: str = "support@snt.ai"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8501"]

    postgres_dsn: PostgresDsn = Field(
        default="postgresql+asyncpg://snt:snt@localhost:5432/snt_ai",
        validation_alias="SNT_POSTGRES_DSN",
    )
    postgres_pool_size: int = 20
    postgres_max_overflow: int = 10

    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "snt_ai"

    redis_dsn: RedisDsn = Field(
        default="redis://localhost:6379/0",
        validation_alias="SNT_REDIS_DSN",
    )

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"

    auth_provider: str = "clerk"
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    auth0_domain: str = ""
    auth0_audience: str = ""
    auth0_issuer: str = ""

    encryption_key: str = ""
    jwt_algorithm: str = "RS256"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    vllm_endpoint: str = ""
    vllm_api_key: str = ""

    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "snt-ai-backend"

    judge_model: str = "gpt-4o"
    default_seed: int = 42
    default_failure_rate: float = 0.30
    max_failure_rate: float = 50.0
    corpus_path: str = "synthetic_customers.json"
    report_path: str = "ai_safety_report.txt"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == RuntimeEnvironment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.environment == RuntimeEnvironment.PRODUCTION

    def validate_production_safety(self) -> None:
        """Raise at startup if dangerous defaults are detected in production."""
        if not self.is_production:
            return
        errors: list[str] = []
        if not self.encryption_key or self.encryption_key == "dev-secret-key-change-in-production":
            errors.append("SNT_ENCRYPTION_KEY must be set to a random secret in production")
        if not self.cors_origins or any("localhost" in o for o in self.cors_origins):
            errors.append(
                "SNT_CORS_ORIGINS must not contain 'localhost' in production — "
                f"current value: {self.cors_origins}"
            )
        if self.auth_provider == "local" and self.is_production:
            errors.append(
                "SNT_AUTH_PROVIDER=local uses a dev-only code path. "
                "Use 'clerk' or 'auth0' in production."
            )
        if errors:
            raise RuntimeError(
                "Production safety check FAILED — refusing to start:\n"
                + "\n".join(f"  • {e}" for e in errors)
            )


@lru_cache
def get_config() -> AppConfig:
    cfg = AppConfig()
    cfg.validate_production_safety()
    return cfg

