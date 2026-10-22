from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config.settings import settings
from app.api.accidents import router as accident_router
from app.api.auth import router as auth_router
from app.api.claims import router as claim_router
from app.api.customer_routes import router as customer_router
from app.api.damage_assessments import router as damage_assessment_router
from app.api.inspections import router as inspection_router
from app.api.payments import router as payment_router
from app.api.policy_routes import router as policy_router
from app.api.reports import router as report_router
from app.api.settlements import router as settlement_router
from app.api.surveyors import router as surveyor_router
from app.api.vehicle_routes import router as vehicle_router
from app.database.database import create_db_and_tables
from app.utils.exceptions import (
    ConflictError,
    InvalidStateTransitionError,
    NotFoundError,
    ValidationError,
)

app = FastAPI(
    title="Vehicle Insurance Claim Management System",
    description="Backend API for managing vehicle insurance and claims",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(
    _request: Request, exc: NotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(ConflictError)
@app.exception_handler(InvalidStateTransitionError)
async def conflict_error_handler(
    _request: Request, exc: ConflictError | InvalidStateTransitionError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(
    _request: Request, exc: ValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    _request: Request, _exc: IntegrityError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "Database constraint conflict"},
    )


@app.on_event("startup")
def startup_event():
    create_db_and_tables()


@app.get("/")
def home():
    return {
        "message": "Vehicle Insurance Claim Management System API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(accident_router)
app.include_router(auth_router)
app.include_router(claim_router)
app.include_router(customer_router)
app.include_router(damage_assessment_router)
app.include_router(inspection_router)
app.include_router(vehicle_router)
app.include_router(policy_router)
app.include_router(settlement_router)
app.include_router(payment_router)
app.include_router(report_router)
app.include_router(surveyor_router)
