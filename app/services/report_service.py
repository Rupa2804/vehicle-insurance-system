from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.settlement import Settlement
from app.models.payment import Payment


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def settlement_summary(self):
        result = self.db.query(
            func.count(Settlement.id).label("total_settlements"),
            func.coalesce(
                func.sum(Settlement.estimated_amount), 0
            ).label("total_estimated_amount"),
            func.coalesce(
                func.sum(Settlement.approved_amount), 0
            ).label("total_approved_amount"),
            func.coalesce(
                func.sum(Settlement.final_amount), 0
            ).label("total_final_amount"),
        ).first()

        return {
            "total_settlements": result.total_settlements,
            "total_estimated_amount": result.total_estimated_amount,
            "total_approved_amount": result.total_approved_amount,
            "total_final_amount": result.total_final_amount,
        }

    def settlement_status_report(self):
        results = (
            self.db.query(
                Settlement.status,
                func.count(Settlement.id).label("count"),
                func.coalesce(
                    func.sum(Settlement.final_amount), 0
                ).label("total_amount"),
            )
            .group_by(Settlement.status)
            .all()
        )

        return [
            {
                "status": row.status,
                "count": row.count,
                "total_amount": row.total_amount,
            }
            for row in results
        ]

    def payment_summary(self):
        result = self.db.query(
            func.count(Payment.id).label("total_payments"),
            func.coalesce(
                func.sum(Payment.amount), 0
            ).label("total_amount"),
        ).first()

        return {
            "total_payments": result.total_payments,
            "total_amount": result.total_amount,
        }

    def payment_status_report(self):
        results = (
            self.db.query(
                Payment.status,
                func.count(Payment.id).label("count"),
                func.coalesce(
                    func.sum(Payment.amount), 0
                ).label("total_amount"),
            )
            .group_by(Payment.status)
            .all()
        )

        return [
            {
                "status": row.status,
                "count": row.count,
                "total_amount": row.total_amount,
            }
            for row in results
        ]