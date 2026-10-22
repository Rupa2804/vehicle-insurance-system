from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request
from app.database.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    dependencies=[Depends(authorize_request)],
)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=201
)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db)
):
    try:
        service = PaymentService(db)

        payment = service.create(data)

        db.commit()
        db.refresh(payment)

        return payment

    except ConflictError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    except ValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = PaymentService(db)

        return service.get_by_id(payment_id)

    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/settlement/{settlement_id}",
    response_model=list[PaymentResponse]
)
def get_payments_by_settlement(
    settlement_id: int,
    db: Session = Depends(get_db)
):
    service = PaymentService(db)

    return service.get_by_settlement_id(settlement_id)


@router.post(
    "/{payment_id}/process",
    response_model=PaymentResponse
)
def process_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = PaymentService(db)

        payment = service.process_payment(payment_id)

        db.commit()
        db.refresh(payment)

        return payment

    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/{payment_id}/fail",
    response_model=PaymentResponse
)
def fail_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = PaymentService(db)

        payment = service.mark_failed(payment_id)

        db.commit()
        db.refresh(payment)

        return payment

    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentResponse
)
def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = PaymentService(db)

        payment = service.refund(payment_id)

        db.commit()
        db.refresh(payment)

        return payment

    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{payment_id}"
)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = PaymentService(db)

        result = service.delete(payment_id)

        db.commit()

        return result

    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )