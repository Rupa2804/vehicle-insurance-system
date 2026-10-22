from sqlalchemy.orm import Session

from app.models.surveyor import Surveyor


class SurveyorRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Surveyor:
        surveyor = Surveyor(**data)
        self.db.add(surveyor)
        self.db.flush()
        self.db.refresh(surveyor)
        return surveyor

    def get_by_id(self, surveyor_id: int) -> Surveyor | None:
        return (
            self.db.query(Surveyor)
            .filter(Surveyor.id == surveyor_id)
            .first()
        )

    def get_by_email(self, email: str) -> Surveyor | None:
        return (
            self.db.query(Surveyor)
            .filter(Surveyor.email == email)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Surveyor]:
        return (
            self.db.query(Surveyor)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, surveyor: Surveyor, data: dict) -> Surveyor:
        for key, value in data.items():
            setattr(surveyor, key, value)

        self.db.flush()
        self.db.refresh(surveyor)
        return surveyor

    def delete(self, surveyor: Surveyor) -> None:
        self.db.delete(surveyor)
        self.db.flush()