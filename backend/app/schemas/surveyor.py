from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SurveyorBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    region: str | None = Field(default=None, max_length=100)
    specialization: str | None = Field(default=None, max_length=100)


class SurveyorCreate(SurveyorBase):
    pass


class SurveyorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    region: str | None = Field(default=None, max_length=100)
    specialization: str | None = Field(default=None, max_length=100)
    availability_status: str | None = None


class SurveyorResponse(SurveyorBase):
    id: int
    availability_status: str
    active_claim_count: int

    model_config = ConfigDict(from_attributes=True)