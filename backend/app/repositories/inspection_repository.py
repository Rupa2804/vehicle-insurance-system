from sqlalchemy.orm import Session

from app.models.inspection import Inspection


class InspectionRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Inspection:
        inspection = Inspection(**data)
        self.db.add(inspection)
        self.db.flush()
        self.db.refresh(inspection)
        return inspection

    def get_by_id(self, inspection_id: int) -> Inspection | None:
        return (
            self.db.query(Inspection)
            .filter(Inspection.id == inspection_id)
            .first()
        )

    def get_by_claim_id(self, claim_id: int) -> list[Inspection]:
        return (
            self.db.query(Inspection)
            .filter(Inspection.claim_id == claim_id)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Inspection]:
        return (
            self.db.query(Inspection)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, inspection: Inspection, data: dict) -> Inspection:
        for key, value in data.items():
            setattr(inspection, key, value)

        self.db.flush()
        self.db.refresh(inspection)
        return inspection

    def delete(self, inspection: Inspection) -> None:
        self.db.delete(inspection)
        self.db.flush()