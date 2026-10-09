from decimal import Decimal

from app.repositories.settlement_repository import SettlementRepository
from app.utils.exceptions import NotFoundError, ValidationError


class SettlementService:

    def __init__(self, db):
        self.repo = SettlementRepository(db)

    def create(self, data):
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

        return self.repo.update(
            settlement,
            update_data
        )

    def delete(self, settlement_id: int):
        settlement = self.get_by_id(settlement_id)

        self.repo.delete(settlement)

        return {
            "message": "Settlement deleted successfully"
        }