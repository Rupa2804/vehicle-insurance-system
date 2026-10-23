from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.schemas.common import Password

class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    CLAIMS_OFFICER = "CLAIMS_OFFICER"
    SURVEYOR = "SURVEYOR"
    FINANCE = "FINANCE"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)
    role: UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: Password
    role: UserRole
    customer_id: int | None = Field(default=None, gt=0)
    surveyor_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_customer_link(self) -> "UserCreate":
        if self.role == UserRole.CUSTOMER:
            if self.customer_id is None:
                raise ValueError("Customer accounts must be linked to a customer record")
            if self.surveyor_id is not None:
                raise ValueError("Customer accounts cannot link to a surveyor")
        elif self.role == UserRole.SURVEYOR:
            if self.surveyor_id is None:
                raise ValueError("Surveyor accounts must be linked to a surveyor record")
            if self.customer_id is not None:
                raise ValueError("Surveyor accounts cannot link to a customer")
        elif self.customer_id is not None or self.surveyor_id is not None:
            raise ValueError("Only customer or surveyor accounts may have a linked record")
        return self


class CustomerRegistration(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: Password
    phone: str = Field(pattern=r"^[0-9]{10}$")
    address: str = Field(min_length=3)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    customer_id: int | None
    surveyor_id: int | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
