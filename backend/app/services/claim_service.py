from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.accident import Accident
from app.models.policy import Policy
from app.models.settlement import Settlement
from app.models.vehicle import Vehicle
from app.repositories.claim_repository import ClaimRepository
from app.schemas.claim import ClaimCreate, ClaimStatusUpdate, ClaimUpdate
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError


class ClaimService:

    def __init__(self, db: Session):
        self.repository = ClaimRepository(db)
        self.db = db

    def create_claim(self, data: ClaimCreate):
        claim_data = data.model_dump()
        policy = self.db.get(Policy, data.policy_id)
        if policy is None:
            raise NotFoundError("Policy not found")

        vehicle = self.db.get(Vehicle, data.vehicle_id)
        if vehicle is None:
            raise NotFoundError("Vehicle not found")

        accident = self.db.get(Accident, data.accident_id)
        if accident is None:
            raise NotFoundError("Accident not found")

        if policy.vehicle_id != vehicle.id:
            raise ValidationError("The vehicle is not covered by this policy")
        if accident.vehicle_id != vehicle.id:
            raise ValidationError(
                "The accident does not belong to this vehicle"
            )

        claim_data["claim_number"] = (
            f"CLM-{datetime.now(timezone.utc).strftime('%Y%m%d')}-"
            f"{uuid4().hex[:8].upper()}"
        )

        claim = self.repository.create(claim_data)
        self.db.commit()
        self.db.refresh(claim)

        return claim

    def get_claim(self, claim_id: int):
        claim = self.repository.get_by_id(claim_id)

        if not claim:
            raise NotFoundError("Claim not found")

        return claim

    def get_all_claims(self, skip: int = 0, limit: int = 100):
        if skip < 0 or limit < 1 or limit > 100:
            raise ValueError(
                "skip must be non-negative and limit must be between 1 and 100"
            )

        return self.repository.get_all(skip=skip, limit=limit)

    def update_claim(self, claim_id: int, data: ClaimUpdate):
        claim = self.repository.get_by_id(claim_id)

        if not claim:
            raise NotFoundError("Claim not found")

        update_data = data.model_dump(exclude_unset=True)
        claim = self.repository.update(claim, update_data)

        self.db.commit()
        self.db.refresh(claim)

        return claim

    def update_claim_status(
        self, claim_id: int, data: ClaimStatusUpdate
    ):
        claim = self.repository.get_by_id(claim_id)
        if not claim:
            raise NotFoundError("Claim not found")

        allowed_transitions = {
            "SUBMITTED": {"UNDER_REVIEW"},
            "UNDER_REVIEW": {"APPROVED", "REJECTED"},
        }
        if data.status not in allowed_transitions.get(claim.status, set()):
            raise ConflictError(
                f"Cannot change claim status from {claim.status} to {data.status}"
            )

        claim.status = data.status
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def delete_claim(self, claim_id: int):
        claim = self.repository.get_by_id(claim_id)

        if not claim:
            raise NotFoundError("Claim not found")

        if self.db.query(Settlement.id).filter(
            Settlement.claim_id == claim_id
        ).first():
            raise ConflictError(
                "Cannot delete a claim that has a settlement"
            )

        self.repository.delete(claim)
        self.db.commit()

        return {"message": "Claim deleted successfully"}