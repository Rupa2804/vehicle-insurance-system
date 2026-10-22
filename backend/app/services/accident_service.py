from sqlalchemy.orm import Session

from app.repositories.accident_repository import AccidentRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.accident import AccidentCreate, AccidentUpdate
from app.utils.exceptions import NotFoundError, ValidationError


class AccidentService:

    def __init__(self, db: Session):
        self.repository = AccidentRepository(db)
        self.db = db

    def create_accident(self, data: AccidentCreate):
        accident_data = data.model_dump()
        vehicle = VehicleRepository.get_by_id(
            self.db, accident_data["vehicle_id"]
        )
        if vehicle is None:
            raise NotFoundError("Vehicle not found")

        customer = CustomerRepository.get_by_id(
            self.db, accident_data["customer_id"]
        )
        if customer is None:
            raise NotFoundError("Customer not found")

        if vehicle.customer_id != customer.id:
            raise ValidationError(
                "The vehicle does not belong to this customer"
            )

        accident = self.repository.create(accident_data)
        self.db.commit()
        self.db.refresh(accident)

        return accident

    def get_accident(self, accident_id: int):
        accident = self.repository.get_by_id(accident_id)

        if not accident:
            raise NotFoundError("Accident not found")

        return accident

    def get_all_accidents(self, skip: int = 0, limit: int = 100):
        if skip < 0 or limit < 1 or limit > 100:
            raise ValueError(
                "skip must be non-negative and limit must be between 1 and 100"
            )

        return self.repository.get_all(skip=skip, limit=limit)

    def update_accident(self, accident_id: int, data: AccidentUpdate):
        accident = self.repository.get_by_id(accident_id)

        if not accident:
            raise NotFoundError("Accident not found")

        update_data = data.model_dump(exclude_unset=True)
        accident = self.repository.update(accident, update_data)

        self.db.commit()
        self.db.refresh(accident)

        return accident

    def delete_accident(self, accident_id: int):
        accident = self.repository.get_by_id(accident_id)

        if not accident:
            raise NotFoundError("Accident not found")

        self.repository.delete(accident)
        self.db.commit()

        return {"message": "Accident deleted successfully"}