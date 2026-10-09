from fastapi import FastAPI

from app.api.settlements import router as settlement_router
from app.api.payments import router as payment_router
from app.api.reports import router as report_router


app = FastAPI(
    title="Vehicle Insurance Claim Management System",
    description="Backend API for managing vehicle insurance claims",
    version="1.0.0"
)


app.include_router(settlement_router)
app.include_router(payment_router)
app.include_router(report_router)


@app.get("/")
def root():
    return {
        "message": "Vehicle Insurance Claim Management System API is running"
    }