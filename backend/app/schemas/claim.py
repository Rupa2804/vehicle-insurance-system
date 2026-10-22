from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClaimBase(BaseModel):
    policy_id: int = Field(gt=0)
    vehicle_id: int = Field(gt=0)
    accident_id: int = Field(gt=0)
    claim_type: str = Field(min_length=1, max_length=50)
    claimed_amount: Decimal = Field(gt=0)
    priority: str = "MEDIUM"
    description: str | None = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    claim_type: str | None = Field(default=None, min_length=1, max_length=50)
    claimed_amount: Decimal | None = Field(default=None, gt=0)
    priority: str | None = None
    description: str | None = None


class ClaimStatusUpdate(BaseModel):
    status: Literal["UNDER_REVIEW", "APPROVED", "REJECTED"]


class ClaimResponse(ClaimBase):
    id: int
    claim_number: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)