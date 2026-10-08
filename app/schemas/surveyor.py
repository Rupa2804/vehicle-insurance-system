from pydantic import BaseModel


class SurveyorCreate(BaseModel):

    name: str

    specialization: list[str]

    region: str

    available: bool = True


