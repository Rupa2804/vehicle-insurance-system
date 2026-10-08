from pydantic import BaseModel


class InspectionCreate(BaseModel):
    surveyor_id: str
    front: str
    rear: str
    left_side: str
    right_side: str
    roof: str
    engine: str
    windshield: str
    lights: str
    tyres: str
    damage_severity: str
    damage_summary: str
    estimated_repair_cost: float
    recommendations: str
    inspector_remarks: str