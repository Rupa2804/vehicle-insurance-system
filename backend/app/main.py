from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
from app.config.settings import settings
from app.database.database import create_db_and_tables, engine, get_db
from app.utils.exceptions import (
    ConflictError,
    InvalidStateTransitionError,
    NotFoundError,
    ValidationError,
)

api_prefix = "/api" if os.getenv("VERCEL") == "1" else ""


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.getenv("VERCEL") == "1" and engine.dialect.name == "sqlite":
        raise RuntimeError(
            "Vercel deployments require a persistent database; set DATABASE_URL "
            "to a managed PostgreSQL database."
        )
    if os.getenv("VERCEL") == "1" and (
        len(settings.JWT_SECRET_KEY) < 32
        or "replace_with" in settings.JWT_SECRET_KEY.lower()
    ):
        raise RuntimeError(
            "Vercel deployments require a private JWT_SECRET_KEY of at least "
            "32 characters."
        )
    create_db_and_tables()
    yield


app = FastAPI(
    title="Vehicle Insurance Claim Management System",
    description="Backend API for managing vehicle insurance and claims",
    version="1.0.0",
    lifespan=lifespan,
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


@app.get("/", include_in_schema=False)
def home(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/login")
    return {
        "message": "Vehicle Insurance Claim Management System API is running"
    }


@app.get(f"{api_prefix}/health")
def health_check():
    return {"status": "ok"}


@app.get(f"{api_prefix}/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


app.include_router(accident_router, prefix=api_prefix)
app.include_router(auth_router, prefix=api_prefix)
app.include_router(claim_router, prefix=api_prefix)
app.include_router(customer_router, prefix=api_prefix)
app.include_router(damage_assessment_router, prefix=api_prefix)
app.include_router(inspection_router, prefix=api_prefix)
app.include_router(vehicle_router, prefix=api_prefix)
app.include_router(policy_router, prefix=api_prefix)
app.include_router(settlement_router, prefix=api_prefix)
app.include_router(payment_router, prefix=api_prefix)
app.include_router(report_router, prefix=api_prefix)
app.include_router(surveyor_router, prefix=api_prefix)
app.frontend(
    "/",
    directory="frontend/dist",
    fallback="index.html",
    check_dir=False,
)
