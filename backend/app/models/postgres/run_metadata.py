from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy import JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import RunStatus
from app.core.database import Base


class RunMetadata(Base):
    __tablename__ = "run_metadata"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suite_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("evaluation_suites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("target_agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    triggered_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="run_status_enum", create_constraint=True),
        default=RunStatus.PENDING,
        nullable=False,
    )
    total_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    aggregate_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    organization = relationship("Organization", back_populates="run_metadata")
    evaluation_suite = relationship("EvaluationSuite", back_populates="run_metadata")
    target_agent = relationship("TargetAgent", back_populates="run_metadata")

    def __repr__(self) -> str:
        return f"<RunMetadata {self.id} [{self.status.value}]>"
