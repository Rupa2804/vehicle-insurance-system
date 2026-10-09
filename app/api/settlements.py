from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.settlement import SettlementCreate, SettlementResponse
from app.services.settlement_service import SettlementService
from app.utils.exceptions import NotFoundError, ValidationError


router = APIRouter(
    prefix="/settlements",
    tags=["Settlements"]
)


@router.post(
    "/",
    response_model=SettlementResponse,
    status_code=201
)
def create_settlement(
    data: SettlementCreate,
    db: Session = Depends(get_db)
):
    try:
        service = SettlementService(db)
        settlement = service.create(data)

        db.commit()
        db.refresh(settlement)

        return settlement

    except ValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/{settlement_id}",
    response_model=SettlementResponse
)
def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = SettlementService(db)
        return service.get_by_id(settlement_id)

    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/claim/{claim_id}",
    response_model=SettlementResponse
)
def get_settlement_by_claim(
    claim_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = SettlementService(db)
        return service.get_by_claim_id(claim_id)

    except NotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{settlement_id}",
    response_model=SettlementResponse
)
def update_settlement(
    settlement_id: int,
    data: SettlementCreate,
    db: Session = Depends(get_db)
):
    try:
        service = SettlementService(db)

        settlement = service.update(
            settlement_id,
            data
        )

        db.commit()
        db.refresh(settlement)

        return settlement

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
    "/{settlement_id}"
)
def delete_settlement(
    settlement_id: int,
    db: Session = Depends(get_db)
):
    try:
        service = SettlementService(db)

        result = service.delete(settlement_id)

        db.commit()

        return result

    except NotFoundError as e:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )