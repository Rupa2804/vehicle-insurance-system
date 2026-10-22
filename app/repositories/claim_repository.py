from sqlalchemy.orm import Session

from app.models.claim import Claim


class ClaimRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Claim:
        claim = Claim(**data)
        self.db.add(claim)
        self.db.flush()
        self.db.refresh(claim)
        return claim

    def get_by_id(self, claim_id: int) -> Claim | None:
        return (
            self.db.query(Claim)
            .filter(Claim.id == claim_id)
            .first()
        )

    def get_by_claim_number(self, claim_number: str) -> Claim | None:
        return (
            self.db.query(Claim)
            .filter(Claim.claim_number == claim_number)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Claim]:
        return (
            self.db.query(Claim)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, claim: Claim, data: dict) -> Claim:
        for key, value in data.items():
            setattr(claim, key, value)

        self.db.flush()
        self.db.refresh(claim)
        return claim

    def delete(self, claim: Claim) -> None:
        self.db.delete(claim)
        self.db.flush()