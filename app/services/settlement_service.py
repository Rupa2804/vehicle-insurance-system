from decimal import Decimal

from app.repositories.payment_repository import PaymentRepository
from app.repositories.settlement_repository import SettlementRepository
from app.repositories.claim_repository import ClaimRepository
from app.utils.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


class SettlementService:

    def __init__(self, db):
        self.repo = SettlementRepository(db)
        self.claim_repo = ClaimRepository(db)
        self.payment_repo = PaymentRepository(db)

    def create(self, data):
        if not self.claim_repo.get_by_id(data.claim_id):
            raise NotFoundError("Claim not found")
        if self.repo.get_by_claim_id(data.claim_id):
            raise ConflictError("A settlement already exists for this claim")

        if data.estimated_amount <= 0:
            raise ValidationError(
                "Estimated amount must be greater than zero"
            )

        if data.approved_amount < 0:
            raise ValidationError(
                "Approved amount cannot be negative"
            )

        if data.deductible < 0:
            raise ValidationError(
                "Deductible cannot be negative"
            )

        if data.coverage_limit <= 0:
            raise ValidationError(
                "Coverage limit must be greater than zero"
            )

        # Apply deductible
        eligible_amount = (
            data.approved_amount - data.deductible
        )

        if eligible_amount < 0:
            eligible_amount = Decimal("0.00")

        # Settlement cannot exceed coverage limit
        final_amount = min(
            eligible_amount,
            data.coverage_limit
        )

        values = data.model_dump()

        # Use the calculated value instead of trusting the client
        values["final_amount"] = final_amount

        return self.repo.create(values)

    def get_by_id(self, settlement_id: int):
        settlement = self.repo.get_by_id(settlement_id)

        if not settlement:
            raise NotFoundError(
                "Settlement not found"
            )

        return settlement

    def get_by_claim_id(self, claim_id: int):
        settlement = self.repo.get_by_claim_id(claim_id)

        if not settlement:
            raise NotFoundError(
                "Settlement not found for this claim"
            )

        return settlement

    def update(self, settlement_id: int, data):
        settlement = self.get_by_id(settlement_id)

        update_data = data.model_dump(
            exclude_unset=True
        )
        claim_id = update_data.get("claim_id", settlement.claim_id)
        if not self.claim_repo.get_by_id(claim_id):
            raise NotFoundError("Claim not found")
        existing = self.repo.get_by_claim_id(claim_id)
        if existing is not None and existing.id != settlement_id:
            raise ConflictError("A settlement already exists for this claim")

        if (
            "deductible" in update_data
            and update_data["deductible"] < 0
        ):
            raise ValidationError(
                "Deductible cannot be negative"
            )

        if (
            "coverage_limit" in update_data
            and update_data["coverage_limit"] <= 0
        ):
            raise ValidationError(
                "Coverage limit must be greater than zero"
            )

        approved_amount = update_data.get(
            "approved_amount", settlement.approved_amount
        )
        deductible = update_data.get("deductible", settlement.deductible)
        coverage_limit = update_data.get(
            "coverage_limit", settlement.coverage_limit
        )
        update_data["final_amount"] = min(
            max(approved_amount - deductible, Decimal("0.00")),
            coverage_limit,
        )

        return self.repo.update(
            settlement,
            update_data
        )

    def delete(self, settlement_id: int):
        settlement = self.get_by_id(settlement_id)
        if self.payment_repo.get_by_settlement_id(settlement_id):
            raise ConflictError(
                "Cannot delete a settlement that has payment records"
            )

        self.repo.delete(settlement)

        return {
            "message": "Settlement deleted successfully"
        }