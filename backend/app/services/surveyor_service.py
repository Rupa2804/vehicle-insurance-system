from sqlalchemy.orm import Session

from app.repositories.surveyor_repository import SurveyorRepository
from app.schemas.surveyor import SurveyorCreate, SurveyorUpdate
from app.utils.exceptions import ConflictError, NotFoundError


class SurveyorService:

    def __init__(self, db: Session):
        self.repository = SurveyorRepository(db)
        self.db = db

    def create_surveyor(self, data: SurveyorCreate):
        surveyor_data = data.model_dump()
        surveyor_data["email"] = str(surveyor_data["email"])

        if self.repository.get_by_email(surveyor_data["email"]):
            raise ConflictError("A surveyor with this email already exists")

        surveyor = self.repository.create(surveyor_data)
        self.db.commit()
        self.db.refresh(surveyor)

        return surveyor

    def get_surveyor(self, surveyor_id: int):
        surveyor = self.repository.get_by_id(surveyor_id)

        if not surveyor:
            raise NotFoundError("Surveyor not found")

        return surveyor

    def get_all_surveyors(self, skip: int = 0, limit: int = 100):
        if skip < 0 or limit < 1 or limit > 100:
            raise ValueError(
                "skip must be non-negative and limit must be between 1 and 100"
            )

        return self.repository.get_all(skip=skip, limit=limit)

    def update_surveyor(self, surveyor_id: int, data: SurveyorUpdate):
        surveyor = self.repository.get_by_id(surveyor_id)

        if not surveyor:
            raise NotFoundError("Surveyor not found")

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] is not None:
            update_data["email"] = str(update_data["email"])
            existing = self.repository.get_by_email(update_data["email"])

            if existing and existing.id != surveyor_id:
                raise ConflictError("A surveyor with this email already exists")

        surveyor = self.repository.update(surveyor, update_data)
        self.db.commit()
        self.db.refresh(surveyor)

        return surveyor

    def delete_surveyor(self, surveyor_id: int):
        surveyor = self.repository.get_by_id(surveyor_id)

        if not surveyor:
            raise NotFoundError("Surveyor not found")

        if surveyor.active_claim_count > 0:
            raise ConflictError(
                "Cannot delete a surveyor with active claim assignments"
            )

        self.repository.delete(surveyor)
        self.db.commit()

        return {"message": "Surveyor deleted successfully"}