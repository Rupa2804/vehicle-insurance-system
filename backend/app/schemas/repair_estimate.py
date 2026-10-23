from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RepairEstimateBase(BaseModel):
    claim_id: int = Field(gt=0)
    estimated_amount: Decimal = Field(gt=0)
    approved_amount: Decimal | None = Field(default=None, ge=0)
    remarks: str | None = None


class RepairEstimateCreate(RepairEstimateBase):
    pass


class RepairEstimateResponse(RepairEstimateBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)