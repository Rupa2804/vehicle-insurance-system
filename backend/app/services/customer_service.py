
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models.customer import Customer
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:

    @staticmethod
    def create_customer(
        db: Session,
        customer_data: CustomerCreate,
    ) -> Customer:
        email = str(customer_data.email).lower()
        existing_customer = CustomerRepository.get_by_email(
            db,
            email,
        )
        if existing_customer:
            raise ValueError("A customer with this email already exists")

        if db.query(User.id).filter(User.email == email).first():
            raise ValueError("An account with this email already exists")

        customer = Customer(
            name=customer_data.name,
            email=email,
            phone=customer_data.phone,
            address=customer_data.address,
        )
        db.add(customer)
        if customer_data.initial_password:
            db.flush()
            db.add(
                User(
                    email=email,
                    password_hash=hash_password(customer_data.initial_password),
                    role="CUSTOMER",
                    customer=customer,
                )
            )
        db.commit()
        db.refresh(customer)
        return customer

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
        initial_password = update_data.pop("initial_password", None)
        linked_user = (
            db.query(User)
            .filter(User.customer_id == customer_id)
            .first()
        )

        if "email" in update_data and update_data["email"] is not None:
            email = str(update_data["email"]).lower()
            update_data["email"] = email
            existing_customer = CustomerRepository.get_by_email(db, email)

            if existing_customer and existing_customer.id != customer_id:
                raise ValueError("A customer with this email already exists")
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user and (linked_user is None or existing_user.id != linked_user.id):
                raise ValueError("An account with this email already exists")
            if linked_user:
                linked_user.email = email

        if initial_password:
            if linked_user:
                raise ValueError("This customer already has a login account")

            email = str(update_data.get("email", customer.email)).lower()
            if db.query(User.id).filter(User.email == email).first():
                raise ValueError("An account with this email already exists")

        for field, value in update_data.items():
            setattr(customer, field, value)

        if initial_password:
            db.add(
                User(
                    email=str(customer.email).lower(),
                    password_hash=hash_password(initial_password),
                    role="CUSTOMER",
                    customer_id=customer_id,
                )
            )

        db.commit()
        db.refresh(customer)
        return customer
