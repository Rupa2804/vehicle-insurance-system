
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleRepository:

    @staticmethod
    def create(db: Session, vehicle_data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**vehicle_data.model_dump())

        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)

        return vehicle

    @staticmethod
    def get_by_id(db: Session, vehicle_id: int) -> Vehicle | None:
        statement = select(Vehicle).where(Vehicle.id == vehicle_id)
        return db.scalar(statement)

    @staticmethod
    def get_by_registration(
        db: Session,
        registration_number: str,
    ) -> Vehicle | None:
        statement = select(Vehicle).where(
            Vehicle.registration_number == registration_number
        )
        return db.scalar(statement)

    @staticmethod
    def get_by_vin(db: Session, vin: str) -> Vehicle | None:
        statement = select(Vehicle).where(Vehicle.vin == vin)
        return db.scalar(statement)

    @staticmethod
    def get_all(db: Session) -> list[Vehicle]:
        statement = select(Vehicle).order_by(Vehicle.id)
        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        vehicle: Vehicle,
        vehicle_data: VehicleUpdate,
    ) -> Vehicle:
        update_data = vehicle_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(vehicle, field, value)

        db.commit()
        db.refresh(vehicle)

        return vehicle
