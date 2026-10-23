from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError

from app.auth.security import create_access_token, hash_password
from app.database.base import Base
from app.database.database import get_db
from app.models.user import User
from app.schemas.auth import CustomerRegistration, UserCreate
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.payment import PaymentCreate
from app.schemas.repair_estimate import RepairEstimateCreate
from app.schemas.settlement import SettlementCreate
import app.main as main


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    def override_get_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)
    main.app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(main.app, raise_server_exceptions=False) as test_client:
            db = session_factory()
            admin = User(
                email="test-admin@example.com",
                password_hash=hash_password("AdminPassword123!"),
                role="ADMIN",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            test_client.headers["Authorization"] = (
                f"Bearer {create_access_token(admin.id, admin.role)}"
            )
            db.close()
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def create_customer(client: TestClient, email: str = "owner@example.com") -> int:
    response = client.post(
        "/customers/",
        json={
            "name": "Vehicle Owner",
            "email": email,
            "phone": "1234567890",
            "address": "1 Main Street",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_vehicle(client: TestClient, customer_id: int) -> int:
    response = client.post(
        "/vehicles/",
        json={
            "customer_id": customer_id,
            "registration_number": "ABC-123",
            "vin": "VIN-123456789",
            "make": "Example",
            "model": "Model One",
            "manufacture_year": 2022,
            "vehicle_type": "CAR",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_policy(
    client: TestClient, customer_id: int, vehicle_id: int
) -> int:
    response = client.post(
        "/policies/",
        json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "policy_number": "POL-123",
            "policy_type": "COMPREHENSIVE",
            "start_date": "2025-01-01",
            "end_date": "2026-12-31",
            "premium": "1200.00",
            "coverage_limit": "50000.00",
            "deductible": "500.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_password_mobile_and_relationship_id_constraints() -> None:
    registration_data = {
        "name": "Policy Customer",
        "email": "policy.customer@example.com",
        "phone": "1234567890",
        "address": "1 Test Street",
    }
    for password in ("123456789012", "abcdefghijkl", "short123"):
        with pytest.raises(ValidationError):
            CustomerRegistration(**registration_data, password=password)
        with pytest.raises(ValidationError):
            UserCreate(
                email="provisioned@example.com",
                password=password,
                role="AGENT",
            )

    CustomerRegistration(**registration_data, password="customer12345")
    UserCreate(
        email="provisioned@example.com",
        password="agentaccount123",
        role="AGENT",
    )

    for phone in ("123456789", "12345678901", "12345abc90"):
        with pytest.raises(ValidationError):
            CustomerCreate(
                name="Policy Customer",
                email="phone.test@example.com",
                phone=phone,
                address="1 Test Street",
            )
        with pytest.raises(ValidationError):
            CustomerUpdate(phone=phone)

    for model, field_name, values in (
        (
            PaymentCreate,
            "settlement_id",
            {"amount": "1", "payment_method": "CARD", "transaction_reference": "TX-1"},
        ),
        (
            RepairEstimateCreate,
            "claim_id",
            {"estimated_amount": "1"},
        ),
        (
            SettlementCreate,
            "claim_id",
            {
                "estimated_amount": "1",
                "approved_amount": "1",
                "deductible": "0",
                "coverage_limit": "10",
                "final_amount": "1",
            },
        ),
    ):
        with pytest.raises(ValidationError):
            model(**values, **{field_name: -1})


def create_accident(
    client: TestClient, customer_id: int, vehicle_id: int
) -> int:
    response = client.post(
        "/accidents/",
        json={
            "vehicle_id": vehicle_id,
            "customer_id": customer_id,
            "accident_date": "2025-02-01",
            "accident_time": "10:30:00",
            "location": "Main Street",
            "accident_type": "COLLISION",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_claim_graph(client: TestClient) -> dict[str, int]:
    customer_id = create_customer(client)
    vehicle_id = create_vehicle(client, customer_id)
    policy_id = create_policy(client, customer_id, vehicle_id)
    accident_id = create_accident(client, customer_id, vehicle_id)
    response = client.post(
        "/claims/",
        json={
            "policy_id": policy_id,
            "vehicle_id": vehicle_id,
            "accident_id": accident_id,
            "claim_type": "COLLISION",
            "claimed_amount": "5000.00",
        },
    )
    assert response.status_code == 201, response.text
    return {
        "customer_id": customer_id,
        "vehicle_id": vehicle_id,
        "policy_id": policy_id,
        "accident_id": accident_id,
        "claim_id": response.json()["id"],
    }


def login_headers(
    client: TestClient, email: str, password: str, role: str
) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password, "role": role},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_endpoints(client: TestClient) -> None:
    assert client.get("/").status_code == 200
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_cors_preflight(client: TestClient) -> None:
    response = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

    rejected = client.options(
        "/auth/login",
        headers={
            "Origin": "https://unexpected.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert rejected.status_code == 400


def test_login_and_role_access(client: TestClient) -> None:
    assert client.get(
        "/customers/", headers={"Authorization": ""}
    ).status_code == 401
    assert client.get("/auth/me", headers={"Authorization": ""}).status_code == 401
    assert client.get("/auth/users", headers={"Authorization": ""}).status_code == 401
    assert client.get("/auth/users").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/health/ready").status_code == 200
    response = client.post(
        "/auth/login",
        json={
            "email": "test-admin@example.com",
            "password": "AdminPassword123!",
            "role": "ADMIN",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["token_type"] == "bearer"
    assert response.json()["user"]["role"] == "ADMIN"
    assert client.post(
        "/auth/login",
        json={
            "email": "test-admin@example.com",
            "password": "AdminPassword123!",
            "role": "CUSTOMER",
        },
    ).status_code == 401
    assert client.post(
        "/auth/login",
        json={
            "email": "test-admin@example.com",
            "password": "wrong",
            "role": "ADMIN",
        },
    ).status_code == 401
    assert client.post(
        "/auth/login",
        json={"email": "test-admin@example.com", "password": "AdminPassword123!"},
    ).status_code == 422

    customer_id = create_customer(client, "role-customer@example.com")
    other_customer_id = create_customer(client, "other-customer@example.com")
    user_response = client.post(
        "/auth/users",
        json={
            "email": "role-customer@example.com",
            "password": "CustomerPassword123!",
            "role": "CUSTOMER",
            "customer_id": customer_id,
        },
    )
    assert user_response.status_code == 201, user_response.text
    assert client.post(
        "/auth/users",
        json={
            "email": "role-customer@example.com",
            "password": "CustomerPassword123!",
            "role": "CUSTOMER",
            "customer_id": customer_id,
        },
    ).status_code == 409
    assert client.post(
        "/auth/users",
        json={
            "email": "missing-customer-link@example.com",
            "password": "CustomerPassword123!",
            "role": "CUSTOMER",
        },
    ).status_code == 422
    assert client.post(
        "/auth/users",
        json={
            "email": "missing-surveyor@example.com",
            "password": "SurveyorPassword123!",
            "role": "SURVEYOR",
            "surveyor_id": 999,
        },
    ).status_code == 404

    customer_login = client.post(
        "/auth/login",
        json={
            "email": "role-customer@example.com",
            "password": "CustomerPassword123!",
            "role": "AGENT",
        },
    )
    assert customer_login.status_code == 401
    customer_login = client.post(
        "/auth/login",
        json={
            "email": "role-customer@example.com",
            "password": "CustomerPassword123!",
            "role": "CUSTOMER",
        },
    )
    assert customer_login.status_code == 200, customer_login.text
    customer_token = customer_login.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    assert client.get("/auth/me", headers=customer_headers).json()["role"] == "CUSTOMER"
    assert client.post("/customers/", json={}, headers=customer_headers).status_code == 403
    assert client.get("/auth/users", headers=customer_headers).status_code == 403
    assert client.patch(
        f"/customers/{customer_id}",
        json={"status": "inactive"},
        headers=customer_headers,
    ).status_code == 403
    customer_records = client.get("/customers/", headers=customer_headers).json()
    assert [record["id"] for record in customer_records] == [customer_id]
    assert client.get(
        f"/customers/{other_customer_id}", headers=customer_headers
    ).status_code == 404

    agent_response = client.post(
        "/auth/users",
        json={
            "email": "role-agent@example.com",
            "password": "AgentPassword123!",
            "role": "AGENT",
        },
    )
    assert agent_response.status_code == 201, agent_response.text
    assert agent_response.status_code == 201, agent_response.text
    agent_login = client.post(
        "/auth/login",
        json={
            "email": "role-agent@example.com",
            "password": "AgentPassword123!",
            "role": "AGENT",
        },
    )
    assert agent_login.status_code == 200, agent_login.text
    agent_token = agent_login.json()["access_token"]
    agent_headers = {"Authorization": f"Bearer {agent_token}"}
    assert client.get("/customers/", headers=agent_headers).status_code == 200
    created_customer = client.post(
        "/customers/",
        json={
            "name": "Agent Added Customer",
            "email": "agent-added-customer@example.com",
            "phone": "1234567890",
            "address": "2 Agent Street",
        },
        headers=agent_headers,
    )
    assert created_customer.status_code == 201, created_customer.text
    assert client.patch(
        f"/customers/{customer_id}",
        json={"status": "inactive"},
        headers=agent_headers,
    ).status_code == 403
    assert client.post("/payments/", json={}, headers=agent_headers).status_code == 403
    assert client.get("/reports/payments/status", headers=agent_headers).status_code == 403
    assert client.get("/inspections/", headers=agent_headers).status_code == 403
    assert client.post(
        "/auth/users",
        json={"email": "agent-created@example.com", "password": "AgentPassword123!", "role": "AGENT"},
        headers=agent_headers,
    ).status_code == 403

    for role, password in (
        ("MANAGER", "ManagerPassword123!"),
        ("CLAIMS_OFFICER", "ClaimsPassword123!"),
        ("FINANCE", "FinancePassword123!"),
    ):
        email = f"{role.lower()}@example.com"
        created = client.post(
            "/auth/users",
            json={"email": email, "password": password, "role": role},
        )
        assert created.status_code == 201, created.text
        headers = login_headers(client, email, password, role)
        assert client.get("/claims/", headers=headers).status_code == 200
        assert client.get("/auth/users", headers=headers).status_code == 403
        if role == "MANAGER":
            assert client.post("/payments/", json={}, headers=headers).status_code == 403
            assert client.post("/claims/", json={}, headers=headers).status_code == 403
        elif role == "CLAIMS_OFFICER":
            assert client.get(
                "/reports/payments/status", headers=headers
            ).status_code == 403
            assert client.post("/claims/", json={}, headers=headers).status_code == 403
            assert client.delete("/claims/1", headers=headers).status_code == 403
            assert client.post("/settlements/", json={}, headers=headers).status_code == 403
            assert client.post(
                "/surveyors/",
                json={"name": "Unauthorized", "email": "unauthorized@example.com"},
                headers=headers,
            ).status_code == 403
        else:
            assert client.get(
                "/reports/payments/status", headers=headers
            ).status_code == 200
            assert client.post("/claims/", json={}, headers=headers).status_code == 403
            assert client.get("/damage-assessments/", headers=headers).status_code == 403
            assert client.patch(
                "/claims/1/status",
                json={"status": "APPROVED"},
                headers=headers,
            ).status_code == 403


def test_customer_vehicle_and_policy_endpoints(client: TestClient) -> None:
    customer_id = create_customer(client)
    assert client.get("/customers/").status_code == 200
    assert client.get(f"/customers/{customer_id}").status_code == 200
    assert client.patch(
        f"/customers/{customer_id}", json={"name": "Updated Owner"}
    ).status_code == 200
    assert client.post(
        "/customers/",
        json={
            "name": "Other Owner",
            "email": "owner@example.com",
            "phone": "1234567890",
            "address": "2 Main Street",
        },
    ).status_code == 409
    assert client.get("/customers/999").status_code == 404
    assert client.patch("/customers/999", json={"name": "Missing"}).status_code == 404

    vehicle_id = create_vehicle(client, customer_id)
    assert client.get("/vehicles/").status_code == 200
    assert client.get(f"/vehicles/{vehicle_id}").status_code == 200
    assert client.patch(
        f"/vehicles/{vehicle_id}", json={"make": "Updated"}
    ).status_code == 200
    assert client.post(
        "/vehicles/",
        json={
            "customer_id": 999,
            "registration_number": "NO-CUSTOMER",
            "vin": "VIN-NO-CUSTOMER",
            "make": "Example",
            "model": "Model One",
            "manufacture_year": 2022,
            "vehicle_type": "CAR",
        },
    ).status_code == 404
    assert client.post(
        "/vehicles/",
        json={
            "customer_id": customer_id,
            "registration_number": "ABC-123",
            "vin": "VIN-DUPLICATE",
            "make": "Example",
            "model": "Model One",
            "manufacture_year": 2022,
            "vehicle_type": "CAR",
        },
    ).status_code == 409
    assert client.get("/vehicles/999").status_code == 404
    assert client.patch("/vehicles/999", json={"make": "Missing"}).status_code == 404

    policy_id = create_policy(client, customer_id, vehicle_id)
    assert client.get("/policies/").status_code == 200
    assert client.get(f"/policies/{policy_id}").status_code == 200
    assert client.patch(
        f"/policies/{policy_id}", json={"premium": "1300.00"}
    ).status_code == 200
    assert client.post(
        "/policies/",
        json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "policy_number": "POL-123",
            "policy_type": "COMPREHENSIVE",
            "start_date": "2025-01-01",
            "end_date": "2026-12-31",
            "premium": "1200.00",
            "coverage_limit": "50000.00",
            "deductible": "500.00",
        },
    ).status_code == 409
    assert client.get("/policies/999").status_code == 404
    assert client.patch("/policies/999", json={"premium": "1300.00"}).status_code == 404


def test_customer_cannot_create_vehicle_records(
    client: TestClient,
) -> None:
    customer_id = create_customer(client, "self-register@example.com")
    account = client.post(
        "/auth/users",
        json={
            "email": "self-register@example.com",
            "password": "CustomerPassword123!",
            "role": "CUSTOMER",
            "customer_id": customer_id,
        },
    )
    assert account.status_code == 201, account.text
    headers = login_headers(
        client, "self-register@example.com", "CustomerPassword123!", "CUSTOMER"
    )

    vehicle_data = {
        "registration_number": "SELF-123",
        "vin": "VIN-SELF-123",
        "make": "Example",
        "model": "Customer Car",
        "manufacture_year": 2023,
        "vehicle_type": "CAR",
    }
    assert client.post("/vehicles/", json=vehicle_data, headers=headers).status_code == 403


def test_public_customer_registration_creates_linked_account(
    client: TestClient,
) -> None:
    payload = {
        "name": "New Customer",
        "email": "new.customer@example.com",
        "password": "CustomerPassword123!",
        "phone": "1234567890",
        "address": "1 New Street",
        "role": "ADMIN",
    }
    response = client.post(
        "/auth/register",
        json=payload,
        headers={"Authorization": ""},
    )

    assert response.status_code == 201, response.text
    account = response.json()
    assert account["user"]["role"] == "CUSTOMER"
    assert account["user"]["customer_id"] is not None

    login = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
            "role": "CUSTOMER",
        },
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["customer_id"] == account["user"]["customer_id"]
    assert client.post(
        "/auth/register",
        json=payload,
        headers={"Authorization": ""},
    ).status_code == 409

    registration_operation = client.get("/openapi.json").json()["paths"][
        "/auth/register"
    ]["post"]
    assert registration_operation["responses"]["201"]
    assert "security" not in registration_operation


def test_agent_created_customer_can_sign_in(client: TestClient) -> None:
    agent_email = "customer-creator@example.com"
    agent_password = "AgentPassword123!"
    agent = client.post(
        "/auth/users",
        json={
            "email": agent_email,
            "password": agent_password,
            "role": "AGENT",
        },
    )
    assert agent.status_code == 201, agent.text
    headers = login_headers(client, agent_email, agent_password, "AGENT")

    customer_email = "Agent.Created.Customer@example.com"
    initial_password = "CustomerInitial123!"
    created = client.post(
        "/customers/",
        json={
            "name": "Agent Created Customer",
            "email": customer_email,
            "phone": "1234567890",
            "address": "42 Agent Street",
            "initial_password": initial_password,
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    assert created.json()["email"] == customer_email.lower()

    login = client.post(
        "/auth/login",
        json={
            "email": customer_email,
            "password": initial_password,
            "role": "CUSTOMER",
        },
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["customer_id"] == created.json()["id"]

    changed_email = "renamed.customer@example.com"
    updated = client.patch(
        f"/customers/{created.json()['id']}",
        json={"email": changed_email},
        headers=headers,
    )
    assert updated.status_code == 200, updated.text
    assert client.post(
        "/auth/login",
        json={
            "email": changed_email,
            "password": initial_password,
            "role": "CUSTOMER",
        },
    ).status_code == 200
    assert client.post(
        "/auth/login",
        json={
            "email": customer_email,
            "password": initial_password,
            "role": "CUSTOMER",
        },
    ).status_code == 401


def test_agent_can_provision_login_for_existing_customer_profile(
    client: TestClient,
) -> None:
    customer_id = create_customer(client, "existing-profile@example.com")
    agent_email = "profile-provisioner@example.com"
    agent_password = "AgentPassword123!"
    assert client.post(
        "/auth/users",
        json={
            "email": agent_email,
            "password": agent_password,
            "role": "AGENT",
        },
    ).status_code == 201
    headers = login_headers(client, agent_email, agent_password, "AGENT")
    initial_password = "ExistingCustomer123!"

    provisioned = client.patch(
        f"/customers/{customer_id}",
        json={"initial_password": initial_password},
        headers=headers,
    )
    assert provisioned.status_code == 200, provisioned.text
    login = client.post(
        "/auth/login",
        json={
            "email": "existing-profile@example.com",
            "password": initial_password,
            "role": "CUSTOMER",
        },
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["customer_id"] == customer_id

    conflict = client.patch(
        f"/customers/{customer_id}",
        json={"initial_password": "AnotherInitial123!"},
        headers=headers,
    )
    assert conflict.status_code == 409


def test_vercel_requires_a_persistent_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setattr(
        main,
        "engine",
        SimpleNamespace(dialect=SimpleNamespace(name="sqlite")),
    )

    with pytest.raises(RuntimeError, match="persistent database"):
        with TestClient(main.app):
            pass


def test_accident_and_claim_endpoints(client: TestClient) -> None:
    graph = create_claim_graph(client)

    assert client.get("/accidents/").status_code == 200
    assert client.get(f"/accidents/{graph['accident_id']}").status_code == 200
    assert client.patch(
        f"/accidents/{graph['accident_id']}", json={"location": "Updated"}
    ).status_code == 200
    assert client.delete(f"/accidents/{graph['accident_id']}").status_code == 409
    deletable_accident_id = create_accident(
        client, graph["customer_id"], graph["vehicle_id"]
    )
    assert client.delete(f"/accidents/{deletable_accident_id}").status_code == 200
    assert client.get(f"/accidents/{deletable_accident_id}").status_code == 404
    assert client.patch("/accidents/999", json={"location": "Missing"}).status_code == 404
    assert client.delete("/accidents/999").status_code == 404
    assert client.post(
        "/accidents/",
        json={
            "vehicle_id": 999,
            "customer_id": graph["customer_id"],
            "accident_date": "2025-02-01",
            "location": "Main Street",
            "accident_type": "COLLISION",
        },
    ).status_code == 404

    assert client.get("/claims/").status_code == 200
    assert client.get(f"/claims/{graph['claim_id']}").status_code == 200
    assert client.patch(
        f"/claims/{graph['claim_id']}", json={"priority": "HIGH"}
    ).status_code == 200
    assert client.delete(f"/claims/{graph['claim_id']}").status_code == 200
    assert client.get(f"/claims/{graph['claim_id']}").status_code == 404
    assert client.patch("/claims/999", json={"priority": "HIGH"}).status_code == 404
    assert client.delete("/claims/999").status_code == 404
    assert client.post(
        "/claims/",
        json={
            "policy_id": 999,
            "vehicle_id": graph["vehicle_id"],
            "accident_id": graph["accident_id"],
            "claim_type": "COLLISION",
            "claimed_amount": "5000.00",
        },
    ).status_code == 404
    assert client.get("/claims/?limit=0").status_code == 422


def test_claims_officer_must_review_before_terminal_decision(
    client: TestClient,
) -> None:
    graph = create_claim_graph(client)
    second_claim = client.post(
        "/claims/",
        json={
            "policy_id": graph["policy_id"],
            "vehicle_id": graph["vehicle_id"],
            "accident_id": graph["accident_id"],
            "claim_type": "COLLISION",
            "claimed_amount": "2500.00",
        },
    )
    assert second_claim.status_code == 201, second_claim.text

    officer = client.post(
        "/auth/users",
        json={
            "email": "status-officer@example.com",
            "password": "OfficerPassword123!",
            "role": "CLAIMS_OFFICER",
        },
    )
    assert officer.status_code == 201, officer.text
    officer_headers = login_headers(
        client, "status-officer@example.com", "OfficerPassword123!", "CLAIMS_OFFICER"
    )
    agent = client.post(
        "/auth/users",
        json={
            "email": "status-agent@example.com",
            "password": "AgentPassword123!",
            "role": "AGENT",
        },
    )
    assert agent.status_code == 201, agent.text
    agent_headers = login_headers(
        client, "status-agent@example.com", "AgentPassword123!", "AGENT"
    )
    claim_id = graph["claim_id"]
    status_path = f"/claims/{claim_id}/status"

    assert client.patch(
        status_path, json={"status": "APPROVED"}, headers=officer_headers
    ).status_code == 409
    review = client.patch(
        status_path,
        json={"status": "UNDER_REVIEW"},
        headers=officer_headers,
    )
    assert review.status_code == 200, review.text
    assert review.json()["status"] == "UNDER_REVIEW"
    approved = client.patch(
        status_path, json={"status": "APPROVED"}, headers=officer_headers
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "APPROVED"
    assert client.patch(
        status_path, json={"status": "REJECTED"}, headers=officer_headers
    ).status_code == 409
    assert client.patch(
        f"/claims/{second_claim.json()['id']}/status",
        json={"status": "UNDER_REVIEW"},
        headers=agent_headers,
    ).status_code == 403

    rejected_claim = client.patch(
        f"/claims/{second_claim.json()['id']}/status",
        json={"status": "UNDER_REVIEW"},
        headers=officer_headers,
    )
    assert rejected_claim.status_code == 200, rejected_claim.text
    rejected_claim = client.patch(
        f"/claims/{second_claim.json()['id']}/status",
        json={"status": "REJECTED"},
        headers=officer_headers,
    )
    assert rejected_claim.status_code == 200, rejected_claim.text
    assert rejected_claim.json()["status"] == "REJECTED"
    assert client.patch(
        f"/claims/{second_claim.json()['id']}/status",
        json={"status": "APPROVED"},
        headers=officer_headers,
    ).status_code == 409
    assert client.patch(
        status_path, json={"status": "PENDING"}, headers=officer_headers
    ).status_code == 422


def test_surveyor_and_inspection_endpoints(client: TestClient) -> None:
    graph = create_claim_graph(client)
    surveyor_data = {
        "name": "Field Surveyor",
        "email": "surveyor@example.com",
        "phone": "1234567890",
        "region": "North",
        "specialization": "Vehicle",
    }
    response = client.post("/surveyors/", json=surveyor_data)
    assert response.status_code == 201, response.text
    surveyor_id = response.json()["id"]
    assert client.get("/surveyors/").status_code == 200
    assert client.get(f"/surveyors/{surveyor_id}").status_code == 200
    assert client.patch(
        f"/surveyors/{surveyor_id}", json={"region": "South"}
    ).status_code == 200
    assert client.post("/surveyors/", json=surveyor_data).status_code == 409
    assert client.get("/surveyors/999").status_code == 404
    assert client.patch("/surveyors/999", json={"region": "South"}).status_code == 404
    assert client.delete(f"/surveyors/{surveyor_id}").status_code == 200
    assert client.delete("/surveyors/999").status_code == 404

    surveyor_data["email"] = "assigned@example.com"
    response = client.post("/surveyors/", json=surveyor_data)
    assert response.status_code == 201, response.text
    surveyor_id = response.json()["id"]
    inspection_data = {
        "claim_id": graph["claim_id"],
        "surveyor_id": surveyor_id,
        "inspection_date": "2025-03-01T10:00:00",
        "vehicle_condition": "Damaged",
    }
    response = client.post("/inspections/", json=inspection_data)
    assert response.status_code == 201, response.text
    inspection_id = response.json()["id"]
    unrelated_account = client.post(
        "/auth/users",
        json={
            "email": "unrelated-surveyor-test@example.com",
            "password": "UnrelatedPassword123!",
            "role": "AGENT",
        },
    )
    assert unrelated_account.status_code == 201, unrelated_account.text
    surveyor_user = client.post(
        "/auth/users",
        json={
            "email": "assigned-surveyor@example.com",
            "password": "SurveyorPassword123!",
            "role": "SURVEYOR",
            "surveyor_id": surveyor_id,
        },
    )
    assert surveyor_user.status_code == 201, surveyor_user.text
    assert surveyor_user.json()["id"] != surveyor_id
    surveyor_headers = login_headers(
        client, "assigned-surveyor@example.com", "SurveyorPassword123!", "SURVEYOR"
    )
    assert client.get("/policies/", headers=surveyor_headers).status_code == 403
    assert client.post("/claims/", json={}, headers=surveyor_headers).status_code == 403
    other_accident_id = create_accident(
        client, graph["customer_id"], graph["vehicle_id"]
    )
    other_claim = client.post(
        "/claims/",
        json={
            "policy_id": graph["policy_id"],
            "vehicle_id": graph["vehicle_id"],
            "accident_id": other_accident_id,
            "claim_type": "COLLISION",
            "claimed_amount": "1500.00",
        },
    )
    assert other_claim.status_code == 201, other_claim.text
    other_claim_id = other_claim.json()["id"]
    assigned_claims = client.get("/claims/", headers=surveyor_headers)
    assert assigned_claims.status_code == 200
    assert [claim["id"] for claim in assigned_claims.json()] == [graph["claim_id"]]
    assert client.get(
        f"/claims/{other_claim_id}", headers=surveyor_headers
    ).status_code == 404
    assigned_inspections = client.get("/inspections/", headers=surveyor_headers)
    assert assigned_inspections.status_code == 200
    assert [item["id"] for item in assigned_inspections.json()] == [inspection_id]
    assert client.get(
        f"/inspections/claim/{other_claim_id}", headers=surveyor_headers
    ).status_code == 404
    assert client.post(
        "/damage-assessments/",
        json={
            "claim_id": other_claim_id,
            "component": "Window",
            "damage_type": "Crack",
            "severity": "LOW",
            "estimated_cost": "100.00",
        },
        headers=surveyor_headers,
    ).status_code == 404
    assigned_assessment = client.post(
        "/damage-assessments/",
        json={
            "claim_id": graph["claim_id"],
            "component": "Front bumper",
            "damage_type": "Dent",
            "severity": "MODERATE",
            "estimated_cost": "2500.00",
        },
        headers=surveyor_headers,
    )
    assert assigned_assessment.status_code == 201, assigned_assessment.text
    assessment_id = assigned_assessment.json()["id"]
    assert client.patch(
        f"/inspections/{inspection_id}",
        json={"surveyor_id": 999},
        headers=surveyor_headers,
    ).status_code == 403
    assert client.patch(
        f"/damage-assessments/{assessment_id}",
        json={"approved_cost": "100.00"},
        headers=surveyor_headers,
    ).status_code == 403
    assert client.post(
        f"/damage-assessments/{assessment_id}/approve",
        json={"approved_cost": "100.00"},
        headers=surveyor_headers,
    ).status_code == 403
    assert client.get(f"/surveyors/{surveyor_id}").json()[
        "availability_status"
    ] == "BUSY"
    assert client.delete(f"/surveyors/{surveyor_id}").status_code == 409
    replacement_surveyor = {
        **surveyor_data,
        "email": "replacement@example.com",
    }
    response = client.post("/surveyors/", json=replacement_surveyor)
    assert response.status_code == 201, response.text
    replacement_surveyor_id = response.json()["id"]
    assert client.get("/inspections/").status_code == 200
    assert client.get(f"/inspections/{inspection_id}").status_code == 200
    assert client.get(f"/inspections/claim/{graph['claim_id']}").status_code == 200
    assert client.patch(
        f"/inspections/{inspection_id}", json={"remarks": "Checked"}
    ).status_code == 200
    response = client.patch(
        f"/inspections/{inspection_id}",
        json={"surveyor_id": replacement_surveyor_id},
    )
    assert response.status_code == 200, response.text
    assert client.get(f"/surveyors/{surveyor_id}").json()[
        "availability_status"
    ] == "AVAILABLE"
    replacement_surveyor_response = client.get(
        f"/surveyors/{replacement_surveyor_id}"
    )
    assert replacement_surveyor_response.json()["active_claim_count"] == 1
    assert client.delete(f"/inspections/{inspection_id}").status_code == 200
    replacement_surveyor_response = client.get(
        f"/surveyors/{replacement_surveyor_id}"
    )
    assert replacement_surveyor_response.json()["availability_status"] == "AVAILABLE"
    assert replacement_surveyor_response.json()["active_claim_count"] == 0
    assert client.get("/inspections/999").status_code == 404
    assert client.get("/inspections/claim/999").status_code == 404
    assert client.patch("/inspections/999", json={"remarks": "Missing"}).status_code == 404
    assert client.delete("/inspections/999").status_code == 404


def test_damage_assessment_endpoints(client: TestClient) -> None:
    graph = create_claim_graph(client)
    response = client.post(
        "/damage-assessments/",
        json={
            "claim_id": graph["claim_id"],
            "component": "Front bumper",
            "damage_type": "Dent",
            "severity": "MODERATE",
            "estimated_cost": "2500.00",
        },
    )
    assert response.status_code == 201, response.text
    assessment_id = response.json()["id"]
    assert client.get("/damage-assessments/").status_code == 200
    assert client.get(f"/damage-assessments/{assessment_id}").status_code == 200
    assert client.get(
        f"/damage-assessments/claim/{graph['claim_id']}"
    ).status_code == 200
    assert client.patch(
        f"/damage-assessments/{assessment_id}", json={"remarks": "Reviewed"}
    ).status_code == 200
    officer = client.post(
        "/auth/users",
        json={
            "email": "assessment-officer@example.com",
            "password": "OfficerPassword123!",
            "role": "CLAIMS_OFFICER",
        },
    )
    assert officer.status_code == 201, officer.text
    officer_headers = login_headers(
        client, "assessment-officer@example.com", "OfficerPassword123!", "CLAIMS_OFFICER"
    )
    response = client.post(
        f"/damage-assessments/{assessment_id}/approve",
        json={"approved_cost": "2000.00"},
        headers=officer_headers,
    )
    assert response.status_code == 200, response.text
    assert client.delete(f"/damage-assessments/{assessment_id}").status_code == 400
    assert client.get("/damage-assessments/999").status_code == 404
    assert client.get("/damage-assessments/claim/999").status_code == 404
    assert client.patch(
        "/damage-assessments/999", json={"remarks": "Missing"}
    ).status_code == 404
    assert client.post(
        "/damage-assessments/999/approve", json={"approved_cost": "1.00"}
    ).status_code == 404
    assert client.delete("/damage-assessments/999").status_code == 404
    assert client.post(
        "/damage-assessments/",
        json={
            "claim_id": 999,
            "component": "Window",
            "damage_type": "Crack",
            "severity": "LOW",
            "estimated_cost": "100.00",
        },
    ).status_code == 404


def test_settlement_payment_and_report_endpoints(client: TestClient) -> None:
    graph = create_claim_graph(client)
    settlement_data = {
        "claim_id": graph["claim_id"],
        "estimated_amount": "5000.00",
        "approved_amount": "4000.00",
        "deductible": "500.00",
        "coverage_limit": "3000.00",
        "final_amount": "4000.00",
    }
    finance = client.post(
        "/auth/users",
        json={
            "email": "settlement-finance@example.com",
            "password": "FinancePassword123!",
            "role": "FINANCE",
        },
    )
    assert finance.status_code == 201, finance.text
    finance_headers = login_headers(
        client, "settlement-finance@example.com", "FinancePassword123!", "FINANCE"
    )
    assert client.get(
        f"/claims/{graph['claim_id']}", headers=finance_headers
    ).status_code == 404
    assert client.post(
        "/settlements/", json=settlement_data, headers=finance_headers
    ).status_code == 409
    status_path = f"/claims/{graph['claim_id']}/status"
    assert client.patch(
        status_path, json={"status": "UNDER_REVIEW"}
    ).status_code == 200
    assert client.patch(
        status_path, json={"status": "APPROVED"}
    ).status_code == 200
    assert client.get(
        f"/claims/{graph['claim_id']}", headers=finance_headers
    ).status_code == 200
    response = client.post(
        "/settlements/", json=settlement_data, headers=finance_headers
    )
    assert response.status_code == 201, response.text
    settlement_id = response.json()["id"]
    assert response.json()["final_amount"] == "3000.00"
    assert client.get(f"/settlements/{settlement_id}").status_code == 200
    assert client.get(
        f"/settlements/claim/{graph['claim_id']}"
    ).status_code == 200
    response = client.put(
        f"/settlements/{settlement_id}",
        json=settlement_data,
        headers=finance_headers,
    )
    assert response.status_code == 200
    assert response.json()["final_amount"] == "3000.00"
    assert client.get("/settlements/999").status_code == 404
    assert client.get("/settlements/claim/999").status_code == 404
    assert client.put("/settlements/999", json=settlement_data).status_code == 404
    assert client.post(
        "/settlements/", json={**settlement_data, "claim_id": 999}
    ).status_code == 404
    assert client.post("/settlements/", json=settlement_data).status_code == 409

    payment_data = {
        "settlement_id": settlement_id,
        "amount": "2500.00",
        "payment_method": "BANK_TRANSFER",
        "transaction_reference": "TXN-1",
        "status": "SUCCESS",
    }
    response = client.post(
        "/payments/", json=payment_data, headers=finance_headers
    )
    assert response.status_code == 201, response.text
    payment_id = response.json()["id"]
    assert response.json()["status"] == "PENDING"
    assert client.get(f"/payments/{payment_id}").status_code == 200
    assert client.get(
        f"/payments/settlement/{settlement_id}"
    ).status_code == 200
    response = client.post(
        f"/payments/{payment_id}/process", headers=finance_headers
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "SUCCESS"
    assert client.post(
        f"/payments/{payment_id}/refund", headers=finance_headers
    ).status_code == 200
    assert client.post(
        f"/payments/{payment_id}/process", headers=finance_headers
    ).status_code == 409
    assert client.post("/payments/", json=payment_data).status_code == 409
    assert client.post(
        "/payments/",
        json={
            **payment_data,
            "settlement_id": 999,
            "transaction_reference": "TXN-2",
        },
    ).status_code == 404

    failed_payment_data = {**payment_data, "transaction_reference": "TXN-3"}
    response = client.post("/payments/", json=failed_payment_data)
    assert response.status_code == 201, response.text
    failed_payment_id = response.json()["id"]
    assert client.post(
        f"/payments/{failed_payment_id}/fail", headers=finance_headers
    ).status_code == 200
    assert client.post(
        f"/payments/{failed_payment_id}/refund", headers=finance_headers
    ).status_code == 409
    assert client.get("/payments/999").status_code == 404
    assert client.post("/payments/999/process").status_code == 404
    assert client.post("/payments/999/fail").status_code == 404
    assert client.post("/payments/999/refund").status_code == 404
    assert client.get("/payments/settlement/999").status_code == 404
    assert client.delete(f"/payments/{failed_payment_id}").status_code == 200
    assert client.delete("/payments/999").status_code == 404

    assert client.get("/reports/settlements/summary").status_code == 200
    assert client.get("/reports/settlements/status").status_code == 200
    assert client.get("/reports/payments/summary").status_code == 200
    assert client.get("/reports/payments/status").status_code == 200
    assert client.delete(f"/settlements/{settlement_id}").status_code == 409
    assert client.delete(f"/payments/{payment_id}").status_code == 200
    assert client.delete(f"/settlements/{settlement_id}").status_code == 200
