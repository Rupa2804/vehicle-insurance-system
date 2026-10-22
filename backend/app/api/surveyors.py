from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.surveyor import Surveyor
from app.models.user import User
from app.schemas.surveyor import (
    SurveyorCreate,
    SurveyorResponse,
    SurveyorUpdate,
)
from app.services.surveyor_service import SurveyorService

router = APIRouter(
    prefix="/surveyors",
    tags=["Surveyors"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=SurveyorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_surveyor(
    data: SurveyorCreate,
    db: Session = Depends(get_db),
):
    service = SurveyorService(db)

    try:
        return service.create_surveyor(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[SurveyorResponse])
def get_all_surveyors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = SurveyorService(db)

    try:
        if user.role == "MANAGER":
            return db.query(Surveyor).offset(skip).limit(limit).all()
        return service.get_all_surveyors(skip, limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{surveyor_id}", response_model=SurveyorResponse)
def get_surveyor(
    surveyor_id: int,
    db: Session = Depends(get_db),
):
    service = SurveyorService(db)

    try:
        return service.get_surveyor(surveyor_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{surveyor_id}", response_model=SurveyorResponse)
def update_surveyor(
    surveyor_id: int,
    data: SurveyorUpdate,
    db: Session = Depends(get_db),
):
    service = SurveyorService(db)

    try:
        return service.update_surveyor(surveyor_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{surveyor_id}")
def delete_surveyor(
    surveyor_id: int,
    db: Session = Depends(get_db),
):
    service = SurveyorService(db)

    try:
        return service.delete_surveyor(surveyor_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc