from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    settlement_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(min_length=1, max_length=30)
    transaction_reference: str = Field(min_length=1, max_length=100)
    status: str = "PENDING"
    paid_at: datetime | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)