from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    claim_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    policy_id: Mapped[int] = mapped_column(
        ForeignKey("policies.id"), nullable=False, index=True
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False, index=True
    )

    accident_id: Mapped[int] = mapped_column(
        ForeignKey("accidents.id"), nullable=False, index=True
    )

    claim_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    claimed_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50), default="SUBMITTED", nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20), default="MEDIUM", nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )