from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DamageAssessmentBase(BaseModel):
    claim_id: int = Field(gt=0)
    component: str = Field(min_length=1, max_length=100)
    damage_type: str = Field(min_length=1, max_length=100)
    severity: str = Field(min_length=1, max_length=30)
    estimated_cost: Decimal = Field(ge=0)
    approved_cost: Decimal | None = Field(default=None, ge=0)
    remarks: str | None = None


class DamageAssessmentCreate(DamageAssessmentBase):
    pass


class DamageAssessmentUpdate(BaseModel):
    component: str | None = Field(default=None, min_length=1, max_length=100)
    damage_type: str | None = Field(default=None, min_length=1, max_length=100)
    severity: str | None = Field(default=None, min_length=1, max_length=30)
    estimated_cost: Decimal | None = Field(default=None, ge=0)
    approved_cost: Decimal | None = Field(default=None, ge=0)
    remarks: str | None = None


class DamageAssessmentResponse(DamageAssessmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)