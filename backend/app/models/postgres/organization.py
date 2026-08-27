from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.config import BillingPlan


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    billing_plan: Mapped[BillingPlan] = mapped_column(
        Enum(BillingPlan, name="billing_plan_enum", create_constraint=True),
        default=BillingPlan.FREE,
        nullable=False,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    users = relationship("User", back_populates="organization", lazy="selectin")
    target_agents = relationship("TargetAgent", back_populates="organization", lazy="selectin")
    evaluation_suites = relationship("EvaluationSuite", back_populates="organization", lazy="selectin")
    run_metadata = relationship("RunMetadata", back_populates="organization", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Organization {self.slug}>"
