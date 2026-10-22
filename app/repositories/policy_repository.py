from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate


class PolicyRepository:

    @staticmethod
    def create(
        db: Session,
        policy_data: PolicyCreate,
    ) -> Policy:
        policy = Policy(**policy_data.model_dump())

        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    @staticmethod
    def get_by_id(
        db: Session,
        policy_id: int,
    ) -> Policy | None:
        statement = select(Policy).where(
            Policy.id == policy_id
        )
        return db.scalar(statement)

    @staticmethod
    def get_by_policy_number(
        db: Session,
        policy_number: str,
    ) -> Policy | None:
        statement = select(Policy).where(
            Policy.policy_number == policy_number
        )
        return db.scalar(statement)

    @staticmethod
    def get_all(db: Session) -> list[Policy]:
        statement = select(Policy).order_by(Policy.id)
        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        policy: Policy,
        policy_data: PolicyUpdate,
    ) -> Policy:
        update_data = policy_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(policy, field, value)

        db.commit()
        db.refresh(policy)

        return policy