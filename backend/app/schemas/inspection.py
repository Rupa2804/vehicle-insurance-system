from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InspectionBase(BaseModel):
    claim_id: int = Field(gt=0)
    surveyor_id: int = Field(gt=0)
    inspection_date: datetime
    vehicle_condition: str | None = None
    damage_summary: str | None = None
    estimated_cost: Decimal | None = Field(default=None, ge=0)
    remarks: str | None = None


class InspectionCreate(InspectionBase):
    pass


class InspectionUpdate(BaseModel):
    surveyor_id: int | None = Field(default=None, gt=0)
    inspection_date: datetime | None = None
    vehicle_condition: str | None = None
    damage_summary: str | None = None
    estimated_cost: Decimal | None = Field(default=None, ge=0)
    remarks: str | None = None
    status: str | None = None


class InspectionResponse(InspectionBase):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)