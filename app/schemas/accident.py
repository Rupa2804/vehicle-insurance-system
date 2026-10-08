from pydantic import BaseModel
from datetime import date, time



class AccidentCreate(BaseModel):
    vehicle_id: str
    customer_id: str
    accident_date: date
    accident_time: time
    location: str
    accident_type: str
    description: str
    police_report_available: bool = False
    third_party_involved: bool = False
    injuries_reported: bool = False