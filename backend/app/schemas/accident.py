from datetime import date, time, datetime

from pydantic import BaseModel, ConfigDict, Field


class AccidentBase(BaseModel):
    vehicle_id: int = Field(gt=0)
    customer_id: int = Field(gt=0)
    accident_date: date
    accident_time: time | None = None
    location: str = Field(min_length=1, max_length=255)
    accident_type: str = Field(min_length=1, max_length=50)
    description: str | None = None
    third_party_involved: bool = False
    police_report_available: bool = False


class AccidentCreate(AccidentBase):
    pass


class AccidentUpdate(BaseModel):
    accident_date: date | None = None
    accident_time: time | None = None
    location: str | None = Field(default=None, min_length=1, max_length=255)
    accident_type: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    third_party_involved: bool | None = None
    police_report_available: bool | None = None


class AccidentResponse(AccidentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)