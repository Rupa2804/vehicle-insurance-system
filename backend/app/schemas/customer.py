
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import Password


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(pattern=r"^[0-9]{10}$")
    address: str = Field(min_length=3)
    initial_password: Password | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=r"^[0-9]{10}$")
    address: str | None = Field(default=None, min_length=3)
    status: str | None = Field(default=None, max_length=20)
    initial_password: Password | None = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    status: str

    model_config = ConfigDict(from_attributes=True)
