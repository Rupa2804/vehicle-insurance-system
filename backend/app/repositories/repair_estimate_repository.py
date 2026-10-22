from sqlalchemy.orm import Session

from app.models.repair_estimate import RepairEstimate


class RepairEstimateRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> RepairEstimate:
        repair_estimate = RepairEstimate(**data)

        self.db.add(repair_estimate)
        self.db.flush()
        self.db.refresh(repair_estimate)

        return repair_estimate

    def get_by_id(self, repair_estimate_id: int) -> RepairEstimate | None:
        return (
            self.db.query(RepairEstimate)
            .filter(RepairEstimate.id == repair_estimate_id)
            .first()
        )

    def get_by_claim_id(self, claim_id: int) -> list[RepairEstimate]:
        return (
            self.db.query(RepairEstimate)
            .filter(RepairEstimate.claim_id == claim_id)
            .all()
        )

    def update(
        self,
        repair_estimate: RepairEstimate,
        data: dict
    ) -> RepairEstimate:

        for key, value in data.items():
            setattr(repair_estimate, key, value)

        self.db.flush()
        self.db.refresh(repair_estimate)

        return repair_estimate

    def delete(self, repair_estimate: RepairEstimate) -> None:
        self.db.delete(repair_estimate)
        self.db.flush()