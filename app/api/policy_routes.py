from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.policy import Policy
from app.models.user import User
from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
)
from app.services.policy_service import PolicyService

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db),
):
    try:
        return PolicyService.create_policy(db, policy_data)

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Policy number or related database constraint conflict",
        ) from error


@router.get("/", response_model=list[PolicyResponse])
def get_all_policies(
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    if user.role == "CUSTOMER":
        return (
            db.query(Policy)
            .filter(Policy.customer_id == user.customer_id)
            .order_by(Policy.id)
            .all()
        )
    if user.role == "FINANCE":
        return db.query(Policy).order_by(Policy.id).all()
    return PolicyService.get_all_policies(db)


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
):
    try:
        return PolicyService.get_policy(db, policy_id)

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: int,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db),
):
    try:
        return PolicyService.update_policy(
            db, policy_id, policy_data
        )

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Policy number or related database constraint conflict",
        ) from error