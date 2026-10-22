
from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.models.customer import Customer


class CustomerService:

    @staticmethod
    def create_customer(
        db: Session,
        customer_data: CustomerCreate,
    ) -> Customer:
        existing_customer = CustomerRepository.get_by_email(
            db,
            str(customer_data.email),
        )

        if existing_customer:
            raise ValueError("A customer with this email already exists")

        return CustomerRepository.create(db, customer_data)

    @staticmethod
    def get_customer(
        db: Session,
        customer_id: int,
    ) -> Customer:
        customer = CustomerRepository.get_by_id(db, customer_id)

        if customer is None:
            raise LookupError("Customer not found")

        return customer

    @staticmethod
    def get_all_customers(db: Session) -> list[Customer]:
        return CustomerRepository.get_all(db)

    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer_data: CustomerUpdate,
    ) -> Customer:
        customer = CustomerService.get_customer(db, customer_id)

        update_data = customer_data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] is not None:
            email = str(update_data["email"])
            existing_customer = CustomerRepository.get_by_email(db, email)

            if existing_customer and existing_customer.id != customer_id:
                raise ValueError("A customer with this email already exists")

        return CustomerRepository.update(db, customer, customer_data)
