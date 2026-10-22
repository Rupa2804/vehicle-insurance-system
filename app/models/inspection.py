from datetime import datetime

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


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id"), nullable=False, index=True
    )

    surveyor_id: Mapped[int] = mapped_column(
        ForeignKey("surveyors.id"), nullable=False, index=True
    )

    inspection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    vehicle_condition: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    damage_summary: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    estimated_cost: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30), default="SCHEDULED", nullable=False
    )