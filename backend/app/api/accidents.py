from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.accident import Accident
from app.models.user import User
from app.schemas.accident import (
    AccidentCreate,
    AccidentResponse,
    AccidentUpdate,
)
from app.services.accident_service import AccidentService

router = APIRouter(
    prefix="/accidents",
    tags=["Accidents"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=AccidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_accident(
    data: AccidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = AccidentService(db)

    try:
        if user.role == "CUSTOMER" and data.customer_id != user.customer_id:
            raise HTTPException(status_code=403, detail="You may only report your own accident")
        return service.create_accident(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[AccidentResponse])
def get_all_accidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    service = AccidentService(db)

    try:
        if user.role == "CUSTOMER":
            return (
                db.query(Accident)
                .filter(Accident.customer_id == user.customer_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        if user.role == "FINANCE":
            return db.query(Accident).offset(skip).limit(limit).all()
        return service.get_all_accidents(skip, limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{accident_id}", response_model=AccidentResponse)
def get_accident(
    accident_id: int,
    db: Session = Depends(get_db),
):
    service = AccidentService(db)

    try:
        return service.get_accident(accident_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{accident_id}", response_model=AccidentResponse)
def update_accident(
    accident_id: int,
    data: AccidentUpdate,
    db: Session = Depends(get_db),
):
    service = AccidentService(db)

    try:
        return service.update_accident(accident_id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/{accident_id}")
def delete_accident(
    accident_id: int,
    db: Session = Depends(get_db),
):
    service = AccidentService(db)

    try:
        return service.delete_accident(accident_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc