from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Payment:
        payment = Payment(**data)

        self.db.add(payment)
        self.db.flush()
        self.db.refresh(payment)

        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

    def get_by_settlement_id(self, settlement_id: int) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.settlement_id == settlement_id)
            .all()
        )

    def get_by_transaction_reference(
        self,
        transaction_reference: str
    ) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(
                Payment.transaction_reference == transaction_reference
            )
            .first()
        )

    def update(
        self,
        payment: Payment,
        data: dict
    ) -> Payment:

        for key, value in data.items():
            setattr(payment, key, value)

        self.db.flush()
        self.db.refresh(payment)

        return payment

    def delete(self, payment: Payment) -> None:
        self.db.delete(payment)
        self.db.flush()