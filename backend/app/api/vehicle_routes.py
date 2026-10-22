
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)
from app.services.vehicle_service import VehicleService

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    try:
        if user.role == "CUSTOMER":
            if user.customer_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Customer account is not linked",
                )
            if (
                vehicle_data.customer_id is not None
                and vehicle_data.customer_id != user.customer_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found",
                )
            vehicle_data = vehicle_data.model_copy(
                update={"customer_id": user.customer_id}
            )
        elif vehicle_data.customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="customer_id is required for this role",
            )
        return VehicleService.create_vehicle(db, vehicle_data)
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
            detail="Duplicate vehicle details or invalid customer reference",
        ) from exc


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    user: User = Depends(authorize_request),
):
    if user.role == "CUSTOMER":
        return list(
            db.scalars(
                select(Vehicle)
                .where(Vehicle.customer_id == user.customer_id)
                .order_by(Vehicle.id)
            ).all()
        )
    if user.role == "FINANCE":
        return db.query(Vehicle).order_by(Vehicle.id).all()
    return VehicleService.get_all_vehicles(db)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    try:
        return VehicleService.get_vehicle(db, vehicle_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
):
    try:
        return VehicleService.update_vehicle(
            db,
            vehicle_id,
            vehicle_data,
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
            detail="Duplicate vehicle details or invalid customer reference",
        ) from exc
