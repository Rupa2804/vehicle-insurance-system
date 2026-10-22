from sqlalchemy.orm import Session

from app.models.settlement import Settlement


class SettlementRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Settlement:
        settlement = Settlement(**data)

        self.db.add(settlement)
        self.db.flush()
        self.db.refresh(settlement)

        return settlement

    def get_by_id(self, settlement_id: int) -> Settlement | None:
        return (
            self.db.query(Settlement)
            .filter(Settlement.id == settlement_id)
            .first()
        )

    def get_by_claim_id(self, claim_id: int) -> Settlement | None:
        return (
            self.db.query(Settlement)
            .filter(Settlement.claim_id == claim_id)
            .first()
        )

    def update(
        self,
        settlement: Settlement,
        data: dict
    ) -> Settlement:

        for key, value in data.items():
            setattr(settlement, key, value)

        self.db.flush()
        self.db.refresh(settlement)

        return settlement

    def delete(self, settlement: Settlement) -> None:
        self.db.delete(settlement)
        self.db.flush()
        