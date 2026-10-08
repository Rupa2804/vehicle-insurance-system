from schemas import AccidentCreate
from datetime import datetime
from uuid import uuid4




class AccidentService:

    def create_accident(
        self,
        data: AccidentCreate
    ):

        accident = {

            "accident_id":
                f"ACC{uuid4().hex[:8].upper()}",

            "vehicle_id":
                data.vehicle_id,

            "customer_id":
                data.customer_id,

            "accident_date":
                data.accident_date.isoformat(),

            "accident_time":
                data.accident_time.isoformat(),

            "location":
                data.location,

            "accident_type":
                data.accident_type.upper(),

            "description":
                data.description,

            "police_report_available":
                data.police_report_available,

            "third_party_involved":
                data.third_party_involved,

            "injuries_reported":
                data.injuries_reported,

            "created_at":
                datetime.utcnow()
        }

        accidents_collection.insert_one(
            accident
        )

        accident.pop("_id", None)

        return accident


    def get_accident(
        self,
        accident_id: str
    ):

        accident = accidents_collection.find_one(
            {
                "accident_id":
                    accident_id
            },
            {
                "_id": 0
            }
        )

        return accident