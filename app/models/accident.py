from datetime import date, time, datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    Date,
    Time,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Accident(Base):
    __tablename__ = "accidents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False, index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), nullable=False, index=True
    )

    accident_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    accident_time: Mapped[time | None] = mapped_column(
        Time, nullable=True
    )

    location: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    accident_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    third_party_involved: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    police_report_available: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )