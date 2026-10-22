from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SettlementBase(BaseModel):
    claim_id: int
    estimated_amount: Decimal = Field(gt=0)
    approved_amount: Decimal = Field(ge=0)
    deductible: Decimal = Field(ge=0)
    coverage_limit: Decimal = Field(gt=0)
    final_amount: Decimal = Field(ge=0)
    status: str = "PENDING"


class SettlementCreate(SettlementBase):
    pass


class SettlementResponse(SettlementBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)