from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

_ROLE_METHODS: dict[str, dict[str, set[str]]] = {
    "CUSTOMER": {
        "customers": {"GET", "PATCH"},
        "vehicles": {"GET"},
        "policies": {"GET"},
        "accidents": {"GET", "POST"},
        "claims": {"GET", "POST"},
        "inspections": {"GET"},
        "damage-assessments": {"GET"},
        "settlements": {"GET"},
        "payments": {"GET"},
    },
    "AGENT": {
        "customers": {"GET", "POST", "PATCH"},
        "vehicles": {"GET", "POST", "PATCH"},
        "policies": {"GET", "POST", "PATCH"},
        "accidents": {"GET", "POST", "PATCH"},
        "claims": {"GET", "POST"},
    },
    "CLAIMS_OFFICER": {
        "customers": {"GET"},
        "vehicles": {"GET"},
        "policies": {"GET"},
        "accidents": {"GET"},
        "claims": {"GET", "PATCH"},
        "surveyors": {"GET"},
        "inspections": {"GET", "POST", "PATCH"},
        "damage-assessments": {"GET", "POST", "PATCH"},
    },
    "SURVEYOR": {
        "claims": {"GET"},
        "inspections": {"GET", "PATCH"},
        "damage-assessments": {"GET", "POST", "PATCH"},
    },
    "FINANCE": {
        "claims": {"GET"},
        "settlements": {"GET", "POST", "PUT"},
        "payments": {"GET", "POST"},
        "reports": {"GET"},
    },
    "MANAGER": {
        "customers": {"GET"},
        "vehicles": {"GET"},
        "policies": {"GET"},
        "accidents": {"GET"},
        "claims": {"GET"},
        "surveyors": {"GET"},
        "inspections": {"GET"},
        "damage-assessments": {"GET"},
        "settlements": {"GET"},
        "payments": {"GET"},
        "reports": {"GET"},
    },
}

_SPECIAL_OPERATIONS: dict[str, dict[str, set[str]]] = {
    "FINANCE": {
        "payments": {
            "POST /payments/{payment_id}/process",
            "POST /payments/{payment_id}/fail",
            "POST /payments/{payment_id}/refund",
        }
    },
    "CLAIMS_OFFICER": {
        "damage-assessments": {
            "POST /damage-assessments/{assessment_id}/approve",
        }
    },
    "ADMIN": {},
}


def _resource(route_path: str) -> str:
    return route_path.strip("/").split("/", 1)[0]


def _operation_allowed(role: str, method: str, route_path: str) -> bool:
    if role == "ADMIN":
        return True
    if route_path == "/auth/me" and method == "GET":
        return True
    operation = f"{method} {route_path}"
    if any(
        operation in operations
        for role_operations in _SPECIAL_OPERATIONS.values()
        for operations in role_operations.values()
    ):
        return any(
            operation in operations
            for operations in _SPECIAL_OPERATIONS.get(role, {}).values()
        )
    if method in _ROLE_METHODS.get(role, {}).get(_resource(route_path), set()):
        return True
    return False


def _customer_id_for_claim(db: Session, claim_id: int) -> int | None:
    from app.models.claim import Claim
    from app.models.vehicle import Vehicle

    row = (
        db.query(Vehicle.customer_id)
        .join(Claim, Claim.vehicle_id == Vehicle.id)
        .filter(Claim.id == claim_id)
        .first()
    )
    return row[0] if row else None


def _customer_id_for_settlement(db: Session, settlement_id: int) -> int | None:
    from app.models.settlement import Settlement

    row = db.query(Settlement.claim_id).filter(
        Settlement.id == settlement_id
    ).first()
    return _customer_id_for_claim(db, row[0]) if row else None


def _customer_id_for_payment(db: Session, payment_id: int) -> int | None:
    from app.models.payment import Payment

    row = db.query(Payment.settlement_id).filter(
        Payment.id == payment_id
    ).first()
    return _customer_id_for_settlement(db, row[0]) if row else None


def _customer_id_for_inspection(db: Session, inspection_id: int) -> int | None:
    from app.models.inspection import Inspection

    row = db.query(Inspection.claim_id).filter(
        Inspection.id == inspection_id
    ).first()
    return _customer_id_for_claim(db, row[0]) if row else None


def _customer_id_for_assessment(db: Session, assessment_id: int) -> int | None:
    from app.models.damage_assessment import DamageAssessment

    row = db.query(DamageAssessment.claim_id).filter(
        DamageAssessment.id == assessment_id
    ).first()
    return _customer_id_for_claim(db, row[0]) if row else None


def _ensure_record_scope(
    request: Request, db: Session, user: User, route_path: str
) -> None:
    from app.models.accident import Accident
    from app.models.customer import Customer
    from app.models.inspection import Inspection
    from app.models.policy import Policy
    from app.models.vehicle import Vehicle

    params = request.path_params
    customer_id = user.customer_id
    if user.role == "CUSTOMER":
        if customer_id is None:
            raise HTTPException(status_code=403, detail="Customer account is not linked")
        if "customer_id" in params:
            record = db.get(Customer, int(params["customer_id"]))
            if record is None or record.id != customer_id:
                raise HTTPException(status_code=404, detail="Customer not found")
        if "vehicle_id" in params:
            record = db.get(Vehicle, int(params["vehicle_id"]))
            if record is None or record.customer_id != customer_id:
                raise HTTPException(status_code=404, detail="Vehicle not found")
        if "policy_id" in params:
            record = db.get(Policy, int(params["policy_id"]))
            if record is None or record.customer_id != customer_id:
                raise HTTPException(status_code=404, detail="Policy not found")
        if "accident_id" in params:
            record = db.get(Accident, int(params["accident_id"]))
            if record is None or record.customer_id != customer_id:
                raise HTTPException(status_code=404, detail="Accident not found")
        if "claim_id" in params:
            if _customer_id_for_claim(db, int(params["claim_id"])) != customer_id:
                raise HTTPException(status_code=404, detail="Claim not found")
        if "inspection_id" in params:
            if _customer_id_for_inspection(
                db, int(params["inspection_id"])
            ) != customer_id:
                raise HTTPException(status_code=404, detail="Inspection not found")
        if "assessment_id" in params:
            if _customer_id_for_assessment(
                db, int(params["assessment_id"])
            ) != customer_id:
                raise HTTPException(status_code=404, detail="Assessment not found")
        if "settlement_id" in params:
            if _customer_id_for_settlement(
                db, int(params["settlement_id"])
            ) != customer_id:
                raise HTTPException(status_code=404, detail="Settlement not found")
        if "payment_id" in params:
            if _customer_id_for_payment(
                db, int(params["payment_id"])
            ) != customer_id:
                raise HTTPException(status_code=404, detail="Payment not found")
        if route_path == "/payments/settlement/{settlement_id}":
            settlement_id = int(params["settlement_id"])
            if _customer_id_for_settlement(db, settlement_id) != customer_id:
                raise HTTPException(status_code=404, detail="Settlement not found")
    elif user.role == "SURVEYOR":
        surveyor_id = user.surveyor_id
        if surveyor_id is None:
            raise HTTPException(
                status_code=403,
                detail="Surveyor account is not linked to a surveyor record",
            )
        if "inspection_id" in params:
            inspection = db.get(Inspection, int(params["inspection_id"]))
            if inspection is None or inspection.surveyor_id != surveyor_id:
                raise HTTPException(status_code=404, detail="Inspection not found")
        if "claim_id" in params and route_path.startswith(
            ("/claims/", "/inspections/claim/", "/damage-assessments/claim/")
        ):
            from app.models.inspection import Inspection as InspectionModel

            assigned = (
                db.query(InspectionModel.id)
                .filter(
                    InspectionModel.claim_id == int(params["claim_id"]),
                    InspectionModel.surveyor_id == surveyor_id,
                )
                .first()
            )
            if assigned is None:
                raise HTTPException(status_code=404, detail="Assigned claim not found")
        if "assessment_id" in params:
            from app.models.damage_assessment import DamageAssessment
            from app.models.inspection import Inspection as InspectionModel

            assessment = db.get(
                DamageAssessment, int(params["assessment_id"])
            )
            assigned = assessment is not None and (
                db.query(InspectionModel.id)
                .filter(
                    InspectionModel.claim_id == assessment.claim_id,
                    InspectionModel.surveyor_id == surveyor_id,
                )
                .first()
                is not None
            )
            if not assigned:
                raise HTTPException(status_code=404, detail="Assessment not found")


async def authorize_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = decode_access_token(credentials.credentials)
    try:
        user_id = int(claims["sub"]) if claims else 0
    except (KeyError, TypeError, ValueError):
        user_id = 0
    user = db.get(User, user_id) if user_id > 0 else None
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    route_path = request.scope["route"].path
    if not _operation_allowed(user.role, request.method, route_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role is not permitted to perform this action",
        )

    _ensure_record_scope(request, db, user, route_path)
    request.state.user = user
    return user


def require_admin() -> Callable:
    async def admin_only(user: User = Depends(authorize_request)) -> User:
        if user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator access required",
            )
        return user

    return admin_only
