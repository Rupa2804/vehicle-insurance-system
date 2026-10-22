
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a customer record",
    description=(
        "Create a customer profile as an authenticated AGENT or ADMIN. "
        "For public customer onboarding, use POST /auth/register; it creates "
        "the customer profile and linked login account together."
    ),
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        return CustomerService.create_customer(db, customer_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists",
        ) from exc


@router.get("/", response_model=list[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    customers = CustomerService.get_all_customers(db)
    if user.role == "CUSTOMER":
        return [customer for customer in customers if customer.id == user.customer_id]
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return CustomerService.get_customer(db, customer_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    try:
        if user.role != "ADMIN" and "status" in customer_data.model_fields_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators may change customer account status",
            )
        return CustomerService.update_customer(
            db,
            customer_id,
            customer_data,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists",
        ) from exc
