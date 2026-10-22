
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.repositories.customer_repository import CustomerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:

    @staticmethod
    def create_vehicle(
        db: Session,
        vehicle_data: VehicleCreate,
    ) -> Vehicle:
        # Check whether the customer exists.
        customer = CustomerRepository.get_by_id(
            db,
            vehicle_data.customer_id,
        )

        if customer is None:
            raise LookupError("Customer not found")

        # Check for duplicate registration number.
        existing_registration = VehicleRepository.get_by_registration(
            db,
            vehicle_data.registration_number,
        )

        if existing_registration:
            raise ValueError("Registration number already exists")

        # Check for duplicate VIN.
        existing_vin = VehicleRepository.get_by_vin(
            db,
            vehicle_data.vin,
        )

        if existing_vin:
            raise ValueError("VIN already exists")

        return VehicleRepository.create(db, vehicle_data)

    @staticmethod
    def get_vehicle(db: Session, vehicle_id: int) -> Vehicle:
        vehicle = VehicleRepository.get_by_id(db, vehicle_id)

        if vehicle is None:
            raise LookupError("Vehicle not found")

        return vehicle

    @staticmethod
    def get_all_vehicles(db: Session) -> list[Vehicle]:
        return VehicleRepository.get_all(db)

    @staticmethod
    def update_vehicle(
        db: Session,
        vehicle_id: int,
        vehicle_data: VehicleUpdate,
    ) -> Vehicle:
        vehicle = VehicleService.get_vehicle(db, vehicle_id)
        update_data = vehicle_data.model_dump(exclude_unset=True)

        # Validate a new customer ID, if supplied.
        if (
            "customer_id" in update_data
            and update_data["customer_id"] is not None
        ):
            customer = CustomerRepository.get_by_id(
                db,
                update_data["customer_id"],
            )

            if customer is None:
                raise LookupError("Customer not found")

        # Validate a new registration number, if supplied.
        if (
            "registration_number" in update_data
            and update_data["registration_number"] is not None
        ):
            existing = VehicleRepository.get_by_registration(
                db,
                update_data["registration_number"],
            )

            if existing and existing.id != vehicle_id:
                raise ValueError("Registration number already exists")

        # Validate a new VIN, if supplied.
        if "vin" in update_data and update_data["vin"] is not None:
            existing = VehicleRepository.get_by_vin(
                db,
                update_data["vin"],
            )

            if existing and existing.id != vehicle_id:
                raise ValueError("VIN already exists")

        return VehicleRepository.update(db, vehicle, vehicle_data)
