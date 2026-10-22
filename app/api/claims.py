from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.accident import Accident
from app.models.claim import Claim
from app.models.policy import Policy
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.claim import (
    ClaimCreate,
    ClaimResponse,
    ClaimStatusUpdate,
    ClaimUpdate,
)
from app.services.claim_service import ClaimService

router = APIRouter(
    prefix="/claims",
    tags=["Claims"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_claim(
    data: ClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = ClaimService(db)

    try:
        if user.role == "CUSTOMER":
            policy = db.get(Policy, data.policy_id)
            vehicle = db.get(Vehicle, data.vehicle_id)
            accident = db.get(Accident, data.accident_id)
            if (
                user.customer_id is None
                or policy is None
                or vehicle is None
                or accident is None
                or policy.customer_id != user.customer_id
                or vehicle.customer_id != user.customer_id
                or accident.customer_id != user.customer_id
            ):
                raise HTTPException(status_code=404, detail="Related record not found")
        return service.create_claim(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[ClaimResponse])
def get_all_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = ClaimService(db)

    try:
        if user.role == "CUSTOMER":
            return (
                db.query(Claim)
                .join(Vehicle, Claim.vehicle_id == Vehicle.id)
                .filter(Vehicle.customer_id == user.customer_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        if user.role == "SURVEYOR":
            from app.models.inspection import Inspection

            return (
                db.query(Claim)
                .join(Inspection, Inspection.claim_id == Claim.id)
                .filter(Inspection.surveyor_id == user.surveyor_id)
                .distinct()
                .offset(skip)
                .limit(limit)
                .all()
            )
        if user.role == "FINANCE":
            return (
                db.query(Claim)
                .filter(Claim.status.in_(("APPROVED", "SETTLED")))
                .offset(skip)
                .limit(limit)
                .all()
            )
        return service.get_all_claims(skip, limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = ClaimService(db)

    try:
        claim = service.get_claim(claim_id)
        if user.role == "FINANCE" and claim.status not in {"APPROVED", "SETTLED"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found",
            )
        return claim
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{claim_id}", response_model=ClaimResponse)
def update_claim(
    claim_id: int,
    data: ClaimUpdate,
    db: Session = Depends(get_db),
):
    service = ClaimService(db)

    try:
        return service.update_claim(claim_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{claim_id}/status", response_model=ClaimResponse)
def update_claim_status(
    claim_id: int,
    data: ClaimStatusUpdate,
    db: Session = Depends(get_db),
):
    return ClaimService(db).update_claim_status(claim_id, data)


@router.delete("/{claim_id}")
def delete_claim(
    claim_id: int,
    db: Session = Depends(get_db),
):
    service = ClaimService(db)

    try:
        return service.delete_claim(claim_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc