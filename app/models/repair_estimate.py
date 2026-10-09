from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RepairEstimate(Base):
    __tablename__ = "repair_estimates"

    id: Mapped[int] = mapped_column(
        Integer,
        nullable= False,
        index= True
    )

    claim_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    estimated_amount: Mapped[Decimal] = mapped_column(
       Numeric(12,2),
       nullable= False
    )

    approved_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12,2),
        nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )