from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Surveyor(Base):
    __tablename__ = "surveyors"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    region: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    specialization: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    availability_status: Mapped[str] = mapped_column(
        String(30), default="AVAILABLE", nullable=False
    )

    active_claim_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )