from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(authorize_request)],
)


@router.get("/settlements/summary")
def settlement_summary(
    db: Session = Depends(get_db)
):
    service = ReportService(db)

    return service.settlement_summary()


@router.get("/settlements/status")
def settlement_status_report(
    db: Session = Depends(get_db)
):
    service = ReportService(db)

    return service.settlement_status_report()


@router.get("/payments/summary")
def payment_summary(
    db: Session = Depends(get_db)
):
    service = ReportService(db)

    return service.payment_summary()


@router.get("/payments/status")
def payment_status_report(
    db: Session = Depends(get_db)
):
    service = ReportService(db)

    return service.payment_status_report()