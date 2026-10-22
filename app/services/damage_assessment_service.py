from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.claim_repository import ClaimRepository
from app.repositories.damage_assessment_repository import (
    DamageAssessmentRepository,
)
from app.schemas.damage_assessment import (
    DamageAssessmentCreate,
    DamageAssessmentUpdate,
)
from app.utils.exceptions import NotFoundError


class DamageAssessmentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = DamageAssessmentRepository(db)
        self.claim_repository = ClaimRepository(db)

    def create_assessment(self, data: DamageAssessmentCreate):
        assessment_data = data.model_dump()

        claim = self.claim_repository.get_by_id(
            assessment_data["claim_id"]
        )
        if not claim:
            raise NotFoundError("Claim not found")

        # Approved cost must be assigned through an authorized review process.
        if assessment_data.get("approved_cost") is not None:
            raise ValueError(
                "Approved cost cannot be set during creation"
            )

        assessment = self.repository.create(assessment_data)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def get_assessment(self, assessment_id: int):
        assessment = self.repository.get_by_id(assessment_id)

        if not assessment:
            raise NotFoundError("Damage assessment not found")

        return assessment

    def get_assessments_for_claim(self, claim_id: int):
        claim = self.claim_repository.get_by_id(claim_id)

        if not claim:
            raise NotFoundError("Claim not found")

        return self.repository.get_by_claim_id(claim_id)

    def get_all_assessments(
        self, skip: int = 0, limit: int = 100
    ):
        if skip < 0 or limit < 1 or limit > 100:
            raise ValueError(
                "skip must be non-negative and limit must be between 1 and 100"
            )

        return self.repository.get_all(skip=skip, limit=limit)

    def update_assessment(
        self,
        assessment_id: int,
        data: DamageAssessmentUpdate,
    ):
        assessment = self.repository.get_by_id(assessment_id)

        if not assessment:
            raise NotFoundError("Damage assessment not found")

        update_data = data.model_dump(exclude_unset=True)

        # Prevent ordinary updates from changing an approved amount.
        if "approved_cost" in update_data:
            raise ValueError(
                "Approved cost must be updated through an authorized approval process"
            )

        assessment = self.repository.update(
            assessment, update_data
        )
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def approve_assessment(
        self,
        assessment_id: int,
        approved_cost: Decimal,
    ):
        assessment = self.repository.get_by_id(assessment_id)

        if not assessment:
            raise NotFoundError("Damage assessment not found")

        if approved_cost < Decimal("0.00"):
            raise ValueError("Approved cost cannot be negative")

        if approved_cost > assessment.estimated_cost:
            raise ValueError(
                "Approved cost cannot exceed the estimated cost"
            )

        assessment = self.repository.update(
            assessment,
            {"approved_cost": approved_cost},
        )
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def delete_assessment(self, assessment_id: int):
        assessment = self.repository.get_by_id(assessment_id)

        if not assessment:
            raise NotFoundError("Damage assessment not found")

        if assessment.approved_cost is not None:
            raise ValueError(
                "An approved assessment cannot be deleted"
            )

        self.repository.delete(assessment)
        self.db.commit()

        return {"message": "Damage assessment deleted successfully"}