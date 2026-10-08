from pydantic import BaseModel


class DamageItem(BaseModel):
    part_name: str
    damage_description: str
    damage_severity: str
    estimated_repair_cost: float


class DamageAssessmentCreate(BaseModel):
    assessed_by: str
    damage_items: list[DamageItem]
    remarks: str