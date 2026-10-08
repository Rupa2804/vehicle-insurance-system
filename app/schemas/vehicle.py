
from pydantic import BaseModel, ConfigDict, Field


class VehicleCreate(BaseModel):
    customer_id: int = Field(gt=0)
    registration_number: str = Field(min_length=1, max_length=20)
    vin: str = Field(min_length=1, max_length=50)
    make: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    manufacture_year: int = Field(ge=1886, le=2100)
    vehicle_type: str = Field(min_length=1, max_length=30)


class VehicleUpdate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    registration_number: str | None = Field(default=None, min_length=1, max_length=20)
    vin: str | None = Field(default=None, min_length=1, max_length=50)
    make: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    manufacture_year: int | None = Field(default=None, ge=1886, le=2100)
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=30)
    status: str | None = Field(default=None, max_length=20)


class VehicleResponse(BaseModel):
    id: int
    customer_id: int
    registration_number: str
    vin: str
    make: str
    model: str
    manufacture_year: int
    vehicle_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)
