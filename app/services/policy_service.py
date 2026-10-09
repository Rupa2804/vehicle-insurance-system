from datetime import date

from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.repositories.customer_repository import CustomerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.policy_repository import PolicyRepository
from app.schemas.policy import PolicyCreate, PolicyUpdate


class PolicyService:

    @staticmethod
    def create_policy(
        db: Session,
        policy_data: PolicyCreate,
    ) -> Policy:

        # Check whether the customer exists
        customer = CustomerRepository.get_by_id(
            db, policy_data.customer_id
        )
        if customer is None:
            raise LookupError("Customer not found")

        # Check whether the vehicle exists
        vehicle = VehicleRepository.get_by_id(
            db, policy_data.vehicle_id
        )
        if vehicle is None:
            raise LookupError("Vehicle not found")

        # Ensure the vehicle belongs to the selected customer
        if vehicle.customer_id != policy_data.customer_id:
            raise ValueError(
                "The vehicle does not belong to this customer"
            )

        # Validate policy dates
        if policy_data.end_date < policy_data.start_date:
            raise ValueError(
                "Policy end date cannot be earlier than start date"
            )

        # Check for duplicate policy numbers
        existing_policy = PolicyRepository.get_by_policy_number(
            db, policy_data.policy_number
        )
        if existing_policy:
            raise ValueError("Policy number already exists")

        return PolicyRepository.create(db, policy_data)

    @staticmethod
    def get_policy(db: Session, policy_id: int) -> Policy:
        policy = PolicyRepository.get_by_id(db, policy_id)

        if policy is None:
            raise LookupError("Policy not found")

        return policy

    @staticmethod
    def get_all_policies(db: Session) -> list[Policy]:
        return PolicyRepository.get_all(db)

    @staticmethod
    def update_policy(
        db: Session,
        policy_id: int,
        policy_data: PolicyUpdate,
    ) -> Policy:

        policy = PolicyService.get_policy(db, policy_id)
        update_data = policy_data.model_dump(exclude_unset=True)

        # Validate customer if it is being changed
        customer_id = update_data.get(
            "customer_id", policy.customer_id
        )
        customer = CustomerRepository.get_by_id(db, customer_id)

        if customer is None:
            raise LookupError("Customer not found")

        # Validate vehicle if it is being changed
        vehicle_id = update_data.get(
            "vehicle_id", policy.vehicle_id
        )
        vehicle = VehicleRepository.get_by_id(db, vehicle_id)

        if vehicle is None:
            raise LookupError("Vehicle not found")

        # Ensure the vehicle belongs to the policy's customer
        if vehicle.customer_id != customer_id:
            raise ValueError(
                "The vehicle does not belong to this customer"
            )

        # Validate dates using the updated values and existing values
        start_date = update_data.get(
            "start_date", policy.start_date
        )
        end_date = update_data.get(
            "end_date", policy.end_date
        )

        if start_date is not None and end_date is not None:
            if end_date < start_date:
                raise ValueError(
                    "Policy end date cannot be earlier than start date"
                )

        # Check policy number uniqueness if it is changed
        policy_number = update_data.get("policy_number")

        if policy_number is not None:
            existing_policy = (
                PolicyRepository.get_by_policy_number(
                    db, policy_number
                )
            )

            if existing_policy and existing_policy.id != policy_id:
                raise ValueError("Policy number already exists")

        return PolicyRepository.update(
            db, policy, policy_data
        )