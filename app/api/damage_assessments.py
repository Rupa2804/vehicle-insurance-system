from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.claim import Claim
from app.models.damage_assessment import DamageAssessment
from app.models.inspection import Inspection
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.damage_assessment import (
    DamageAssessmentCreate,
    DamageAssessmentResponse,
    DamageAssessmentUpdate,
)
from app.services.damage_assessment_service import (
    DamageAssessmentService,
)

router = APIRouter(
    prefix="/damage-assessments",
    tags=["Damage Assessments"],
    dependencies=[Depends(authorize_request)],
)


class AssessmentApprovalRequest(BaseModel):
    approved_cost: Decimal = Field(ge=0)


@router.post(
    "/",
    response_model=DamageAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    data: DamageAssessmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = DamageAssessmentService(db)

    try:
        if user.role == "SURVEYOR":
            assigned = (
                db.query(Inspection.id)
                .filter(
                    Inspection.claim_id == data.claim_id,
                    Inspection.surveyor_id == user.surveyor_id,
                )
                .first()
            )
            if assigned is None:
                raise HTTPException(status_code=404, detail="Assigned claim not found")
        return service.create_assessment(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[DamageAssessmentResponse])
def get_all_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = DamageAssessmentService(db)

    try:
        if user.role == "CUSTOMER":
            return (
                db.query(DamageAssessment)
                .join(Claim, DamageAssessment.claim_id == Claim.id)
                .join(Vehicle, Claim.vehicle_id == Vehicle.id)
                .filter(Vehicle.customer_id == user.customer_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        if user.role == "SURVEYOR":
            return (
                db.scalars(
                    select(DamageAssessment)
                    .join(Inspection, Inspection.claim_id == DamageAssessment.claim_id)
                    .where(Inspection.surveyor_id == user.surveyor_id)
                    .distinct()
                    .offset(skip)
                    .limit(limit)
                ).all()
            )
        if user.role == "FINANCE":
            return (
                db.query(DamageAssessment)
                .offset(skip)
                .limit(limit)
                .all()
            )
        return service.get_all_assessments(skip, limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/claim/{claim_id}",
    response_model=list[DamageAssessmentResponse],
)
def get_assessments_for_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = DamageAssessmentService(db)

    try:
        if user.role == "SURVEYOR":
            assigned = (
                db.query(Inspection.id)
                .filter(
                    Inspection.claim_id == claim_id,
                    Inspection.surveyor_id == user.surveyor_id,
                )
                .first()
            )
            if assigned is None:
                raise HTTPException(status_code=404, detail="Assigned claim not found")
            return service.repository.get_by_claim_id(claim_id)
        return service.get_assessments_for_claim(claim_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{assessment_id}",
    response_model=DamageAssessmentResponse,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
):
    service = DamageAssessmentService(db)

    try:
        return service.get_assessment(assessment_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{assessment_id}",
    response_model=DamageAssessmentResponse,
)
def update_assessment(
    assessment_id: int,
    data: DamageAssessmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    if user.role != "ADMIN" and "approved_cost" in data.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Approved costs must be changed through the assessment approval action",
        )
    service = DamageAssessmentService(db)

    try:
        return service.update_assessment(assessment_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{assessment_id}/approve",
    response_model=DamageAssessmentResponse,
)
def approve_assessment(
    assessment_id: int,
    data: AssessmentApprovalRequest,
    db: Session = Depends(get_db),
):
    service = DamageAssessmentService(db)

    try:
        return service.approve_assessment(
            assessment_id,
            data.approved_cost,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{assessment_id}")
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
):
    service = DamageAssessmentService(db)

    try:
        return service.delete_assessment(assessment_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc