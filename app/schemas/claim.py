from pydantic import BaseModel


class ClaimCreate(BaseModel):
    accident_id: str

    vehicle_id: str

    customer_id: str

    policy_id: str

    claim_type: str

    description: str

    claimed_amount: float

    priority: str = "NORMAL"


class ClaimUpdate(BaseModel):

    description: str | None = None

    claimed_amount: float | None = None

    priority: str | None = None