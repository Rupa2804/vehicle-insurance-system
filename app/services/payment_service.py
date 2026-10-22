from datetime import datetime, timezone

from app.repositories.payment_repository import PaymentRepository
from app.repositories.settlement_repository import SettlementRepository
from app.utils.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)


class PaymentService:
    def __init__(self, db):
        self.repo = PaymentRepository(db)
        self.settlement_repo = SettlementRepository(db)

    def create(self, data):
        if data.amount <= 0:
            raise ValidationError("Payment amount must be greater than zero")

        if not self.settlement_repo.get_by_id(data.settlement_id):
            raise NotFoundError("Settlement not found")

        existing_payment = self.repo.get_by_transaction_reference(
            data.transaction_reference
        )

        if existing_payment:
            raise ConflictError(
                "Transaction reference already exists"
            )

        values = data.model_dump()

        # New payments always start as PENDING
        values["status"] = "PENDING"
        values["paid_at"] = None

        return self.repo.create(values)

    def get_by_id(self, payment_id: int):
        payment = self.repo.get_by_id(payment_id)

        if not payment:
            raise NotFoundError("Payment not found")

        return payment

    def get_by_settlement_id(self, settlement_id: int):
        if not self.settlement_repo.get_by_id(settlement_id):
            raise NotFoundError("Settlement not found")
        return self.repo.get_by_settlement_id(settlement_id)

    def process_payment(self, payment_id: int):
        payment = self.get_by_id(payment_id)

        if payment.status == "SUCCESS":
            raise ConflictError(
                "Payment has already been completed"
            )

        if payment.status == "REFUNDED":
            raise ConflictError(
                "Refunded payment cannot be processed"
            )

        # Simulated payment processing
        payment = self.repo.update(
            payment,
            {
                "status": "PROCESSING"
            }
        )

        # In the current project we simulate successful payment
        payment = self.repo.update(
            payment,
            {
                "status": "SUCCESS",
                "paid_at": datetime.now(timezone.utc)
            }
        )

        return payment

    def mark_failed(self, payment_id: int):
        payment = self.get_by_id(payment_id)

        if payment.status == "SUCCESS":
            raise ConflictError(
                "Successful payment cannot be marked as failed"
            )

        payment = self.repo.update(
            payment,
            {
                "status": "FAILED",
                "paid_at": None
            }
        )

        return payment

    def refund(self, payment_id: int):
        payment = self.get_by_id(payment_id)

        if payment.status != "SUCCESS":
            raise ConflictError(
                "Only successful payments can be refunded"
            )

        payment = self.repo.update(
            payment,
            {
                "status": "REFUNDED"
            }
        )

        return payment

    def delete(self, payment_id: int):
        payment = self.get_by_id(payment_id)

        self.repo.delete(payment)

        return {
            "message": "Payment deleted successfully"
        }