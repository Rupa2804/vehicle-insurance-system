from decimal import Decimal

from app.repositories.repair_estimate_repository import (
    RepairEstimateRepository,
)
from app.utils.exceptions import NotFoundError, ValidationError


class RepairEstimateService:

    def __init__(self, db):
        self.repo = RepairEstimateRepository(db)

    def create(self, data):
        if data.estimated_amount <= 0:
            raise ValidationError(
                "Estimated amount must be greater than zero"
            )

        if (
            data.approved_amount is not None
            and data.approved_amount > data.estimated_amount
        ):
            raise ValidationError(
                "Approved amount cannot exceed estimated amount"
            )

        values = data.model_dump()

        return self.repo.create(values)

    def get_by_id(self, repair_estimate_id: int):
        repair_estimate = self.repo.get_by_id(repair_estimate_id)

        if not repair_estimate:
            raise NotFoundError("Repair estimate not found")

        return repair_estimate

    def get_by_claim_id(self, claim_id: int):
        return self.repo.get_by_claim_id(claim_id)

    def update(self, repair_estimate_id: int, data):
        repair_estimate = self.get_by_id(repair_estimate_id)

        update_data = data.model_dump(exclude_unset=True)

        if (
            "estimated_amount" in update_data
            and update_data["estimated_amount"] <= 0
        ):
            raise ValidationError(
                "Estimated amount must be greater than zero"
            )

        estimated_amount = update_data.get(
            "estimated_amount",
            repair_estimate.estimated_amount
        )

        approved_amount = update_data.get(
            "approved_amount",
            repair_estimate.approved_amount
        )

        if (
            approved_amount is not None
            and approved_amount > estimated_amount
        ):
            raise ValidationError(
                "Approved amount cannot exceed estimated amount"
            )

        return self.repo.update(
            repair_estimate,
            update_data
        )

    def delete(self, repair_estimate_id: int):
        repair_estimate = self.get_by_id(repair_estimate_id)

        self.repo.delete(repair_estimate)

        return {"message": "Repair estimate deleted successfully"}