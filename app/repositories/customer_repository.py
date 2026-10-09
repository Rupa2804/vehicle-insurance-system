
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:

    @staticmethod
    def create(db: Session, customer_data: CustomerCreate) -> Customer:
        customer = Customer(
            name=customer_data.name,
            email=str(customer_data.email),
            phone=customer_data.phone,
            address=customer_data.address,
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Customer | None:
        statement = select(Customer).where(Customer.id == customer_id)
        return db.scalar(statement)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        return db.scalar(statement)

    @staticmethod
    def get_all(db: Session) -> list[Customer]:
        statement = select(Customer).order_by(Customer.id)
        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        customer: Customer,
        customer_data: CustomerUpdate,
    ) -> Customer:
        update_data = customer_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(customer, field, str(value) if field == "email" and value is not None else value)

        db.commit()
        db.refresh(customer)

        return customer
