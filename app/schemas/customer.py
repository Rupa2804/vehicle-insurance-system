
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    address: str = Field(min_length=3)


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    address: str | None = Field(default=None, min_length=3)
    status: str | None = Field(default=None, max_length=20)


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    status: str

    model_config = ConfigDict(from_attributes=True)
