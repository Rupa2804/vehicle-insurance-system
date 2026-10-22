from sqlalchemy.orm import Session

from app.repositories.inspection_repository import InspectionRepository
from app.repositories.claim_repository import ClaimRepository
from app.repositories.surveyor_repository import SurveyorRepository
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.utils.exceptions import ConflictError, NotFoundError


class InspectionService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = InspectionRepository(db)
        self.claim_repository = ClaimRepository(db)
        self.surveyor_repository = SurveyorRepository(db)

    def create_inspection(self, data: InspectionCreate):
        inspection_data = data.model_dump()

        claim = self.claim_repository.get_by_id(
            inspection_data["claim_id"]
        )
        if not claim:
            raise NotFoundError("Claim not found")

        surveyor = self.surveyor_repository.get_by_id(
            inspection_data["surveyor_id"]
        )
        if not surveyor:
            raise NotFoundError("Surveyor not found")

        if surveyor.availability_status != "AVAILABLE":
            raise ConflictError("Surveyor is not available")

        inspection = self.repository.create(inspection_data)

        surveyor.active_claim_count += 1
        if surveyor.active_claim_count > 0:
            surveyor.availability_status = "BUSY"

        self.db.commit()
        self.db.refresh(inspection)

        return inspection

    def get_inspection(self, inspection_id: int):
        inspection = self.repository.get_by_id(inspection_id)

        if not inspection:
            raise NotFoundError("Inspection not found")

        return inspection

    def get_inspections_for_claim(self, claim_id: int):
        claim = self.claim_repository.get_by_id(claim_id)
        if not claim:
            raise NotFoundError("Claim not found")

        return self.repository.get_by_claim_id(claim_id)

    def get_all_inspections(self, skip: int = 0, limit: int = 100):
        if skip < 0 or limit < 1 or limit > 100:
            raise ValueError(
                "skip must be non-negative and limit must be between 1 and 100"
            )

        return self.repository.get_all(skip=skip, limit=limit)

    def update_inspection(self, inspection_id: int, data: InspectionUpdate):
        inspection = self.repository.get_by_id(inspection_id)

        if not inspection:
            raise NotFoundError("Inspection not found")

        update_data = data.model_dump(exclude_unset=True)

        if "surveyor_id" in update_data:
            surveyor = self.surveyor_repository.get_by_id(
                update_data["surveyor_id"]
            )
            if not surveyor:
                raise NotFoundError("Surveyor not found")

            if surveyor.id != inspection.surveyor_id:
                if surveyor.availability_status != "AVAILABLE":
                    raise ConflictError("New surveyor is not available")

                previous_surveyor = self.surveyor_repository.get_by_id(
                    inspection.surveyor_id
                )
                if previous_surveyor is not None:
                    previous_surveyor.active_claim_count = max(
                        0, previous_surveyor.active_claim_count - 1
                    )
                    if previous_surveyor.active_claim_count == 0:
                        previous_surveyor.availability_status = "AVAILABLE"

                surveyor.active_claim_count += 1
                surveyor.availability_status = "BUSY"

        inspection = self.repository.update(inspection, update_data)
        self.db.commit()
        self.db.refresh(inspection)

        return inspection

    def delete_inspection(self, inspection_id: int):
        inspection = self.repository.get_by_id(inspection_id)

        if not inspection:
            raise NotFoundError("Inspection not found")

        surveyor = self.surveyor_repository.get_by_id(inspection.surveyor_id)
        if surveyor is not None:
            surveyor.active_claim_count = max(
                0, surveyor.active_claim_count - 1
            )
            if surveyor.active_claim_count == 0:
                surveyor.availability_status = "AVAILABLE"

        self.repository.delete(inspection)
        self.db.commit()

        return {"message": "Inspection deleted successfully"}