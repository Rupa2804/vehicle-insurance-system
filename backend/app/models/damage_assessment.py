from decimal import Decimal

from sqlalchemy import Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DamageAssessment(Base):
    __tablename__ = "damage_assessments"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id"), nullable=False, index=True
    )

    component: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    damage_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    severity: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    approved_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )