from sqlalchemy.orm import Session

from app.models.damage_assessment import DamageAssessment


class DamageAssessmentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> DamageAssessment:
        assessment = DamageAssessment(**data)
        self.db.add(assessment)
        self.db.flush()
        self.db.refresh(assessment)
        return assessment

    def get_by_id(self, assessment_id: int) -> DamageAssessment | None:
        return (
            self.db.query(DamageAssessment)
            .filter(DamageAssessment.id == assessment_id)
            .first()
        )

    def get_by_claim_id(self, claim_id: int) -> list[DamageAssessment]:
        return (
            self.db.query(DamageAssessment)
            .filter(DamageAssessment.claim_id == claim_id)
            .all()
        )

    def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[DamageAssessment]:
        return (
            self.db.query(DamageAssessment)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, assessment: DamageAssessment, data: dict
    ) -> DamageAssessment:
        for key, value in data.items():
            setattr(assessment, key, value)

        self.db.flush()
        self.db.refresh(assessment)
        return assessment

    def delete(self, assessment: DamageAssessment) -> None:
        self.db.delete(assessment)
        self.db.flush()