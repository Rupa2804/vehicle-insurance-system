from sqlalchemy.orm import Session

from app.models.accident import Accident


class AccidentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Accident:
        accident = Accident(**data)
        self.db.add(accident)
        self.db.flush()
        self.db.refresh(accident)
        return accident

    def get_by_id(self, accident_id: int) -> Accident | None:
        return (
            self.db.query(Accident)
            .filter(Accident.id == accident_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Accident]:
        return (
            self.db.query(Accident)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, accident: Accident, data: dict) -> Accident:
        for key, value in data.items():
            setattr(accident, key, value)

        self.db.flush()
        self.db.refresh(accident)
        return accident

    def delete(self, accident: Accident) -> None:
        self.db.delete(accident)
        self.db.flush()