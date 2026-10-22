from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PolicyCreate(BaseModel):
    customer_id: int = Field(gt=0)
    vehicle_id: int = Field(gt=0)
    policy_number: str = Field(min_length=1, max_length=50)
    policy_type: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date
    premium: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    coverage_limit: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    deductible: Decimal = Field(
        ge=0, max_digits=10, decimal_places=2
    )


class PolicyUpdate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    policy_number: str | None = Field(
        default=None, min_length=1, max_length=50
    )
    policy_type: str | None = Field(
        default=None, min_length=1, max_length=50
    )
    start_date: date | None = None
    end_date: date | None = None
    premium: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    coverage_limit: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    deductible: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    status: str | None = Field(default=None, max_length=20)


class PolicyResponse(BaseModel):
    id: int
    customer_id: int
    vehicle_id: int
    policy_number: str
    policy_type: str
    start_date: date
    end_date: date
    premium: Decimal
    coverage_limit: Decimal
    deductible: Decimal
    status: str
    model_config = ConfigDict(from_attributes=True)