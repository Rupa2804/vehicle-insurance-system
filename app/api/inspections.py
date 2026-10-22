from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.claim import Claim
from app.models.inspection import Inspection
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionUpdate,
)
from app.services.inspection_service import InspectionService

router = APIRouter(
    prefix="/inspections",
    tags=["Inspections"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inspection(
    data: InspectionCreate,
    db: Session = Depends(get_db),
):
    service = InspectionService(db)

    try:
        return service.create_inspection(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[InspectionResponse])
def get_all_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = InspectionService(db)

    try:
        if user.role == "CUSTOMER":
            return (
                db.query(Inspection)
                .join(Claim, Inspection.claim_id == Claim.id)
                .join(Vehicle, Claim.vehicle_id == Vehicle.id)
                .filter(Vehicle.customer_id == user.customer_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        if user.role == "SURVEYOR":
            return (
                db.scalars(
                    select(Inspection)
                    .where(Inspection.surveyor_id == user.surveyor_id)
                    .offset(skip)
                    .limit(limit)
                ).all()
            )
        if user.role == "FINANCE":
            return db.query(Inspection).offset(skip).limit(limit).all()
        return service.get_all_inspections(skip, limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
):
    service = InspectionService(db)

    try:
        return service.get_inspection(inspection_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/claim/{claim_id}",
    response_model=list[InspectionResponse],
)
def get_inspections_for_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = InspectionService(db)

    try:
        if user.role == "SURVEYOR":
            return (
                db.query(Inspection)
                .filter(
                    Inspection.claim_id == claim_id,
                    Inspection.surveyor_id == user.surveyor_id,
                )
                .all()
            )
        return service.get_inspections_for_claim(claim_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{inspection_id}", response_model=InspectionResponse)
def update_inspection(
    inspection_id: int,
    data: InspectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    if user.role == "SURVEYOR" and "surveyor_id" in data.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Surveyors cannot reassign inspections",
        )
    service = InspectionService(db)

    try:
        return service.update_inspection(inspection_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{inspection_id}")
def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
):
    service = InspectionService(db)

    try:
        return service.delete_inspection(inspection_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc