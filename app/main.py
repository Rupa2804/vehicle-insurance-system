from fastapi import FastAPI

from app.api.customer_routes import router as customer_router
from app.api.vehicle_routes import router as vehicle_router
from app.api.policy_routes import router as policy_router

app = FastAPI(
    title="Vehicle Insurance Claim Management System",
    description="Backend APIs for managing vehicle insurance and claims",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Vehicle Insurance Claim Management System API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(customer_router)
app.include_router(vehicle_router)
app.include_router(policy_router)