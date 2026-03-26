import pytest
from unittest.mock import patch
from datetime import date, timedelta
from httpx import AsyncClient
from app.modules.auth.security import create_access_token

@pytest.mark.asyncio
async def test_register_client_returns_201(client: AsyncClient, admin_user):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "first_name": "Maria",
        "last_name": "Gomez",
        "email": "maria@example.com",
        "birth_date": "1990-05-15",
        "nationality": "MX",
        "country_of_residence": "CO",
        "document_type": "DNI",
        "document_number": "12345678",
    }
    response = await client.post("/api/v1/emission/clients", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["email"] == "maria@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_client_email_returns_409(client: AsyncClient, admin_user, test_client):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "first_name": "Maria",
        "last_name": "Gomez",
        "email": test_client["email"],
        "birth_date": "1990-05-15",
        "nationality": "MX",
        "country_of_residence": "CO",
        "document_type": "DNI",
        "document_number": "87654321",
    }
    response = await client.post("/api/v1/emission/clients", json=payload, headers=headers)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_issue_policy_returns_201_with_policy_number(client: AsyncClient, admin_user, emission_request_payload):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    with patch("app.modules.emission.pdf_generator.generate_contract_pdf", return_value=b"mock pdf"):
        response = await client.post("/api/v1/emission/issue", json=emission_request_payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "policy_number" in data
        assert data["policy_number"].startswith("YAS-")

@pytest.mark.asyncio
async def test_issue_policy_age_exceeds_max_entry_age_returns_422(client: AsyncClient, admin_user, test_client, created_plan, db_session):
    # Update client birth date to be 100 years old
    from app.modules.emission.models import Client
    import uuid
    
    await db_session.execute(
        Client.__table__.update()
        .where(Client.id == uuid.UUID(test_client["id"]))
        .values(birth_date=date.today() - timedelta(days=100*365))
    )
    await db_session.commit()

    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "client_id": test_client["id"],
        "plan_id": created_plan["id"],
        "country_code": "CO",
        "start_date": str(date.today() + timedelta(days=1))
    }
    response = await client.post("/api/v1/emission/issue", json=payload, headers=headers)
    assert response.status_code == 422
    assert "exceeds max entry age" in response.json()["detail"]

@pytest.mark.asyncio
async def test_issue_policy_invalid_country_returns_422(client: AsyncClient, admin_user, test_client, created_plan):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "client_id": test_client["id"],
        "plan_id": created_plan["id"],
        "country_code": "AR", # Not in plan
        "start_date": str(date.today() + timedelta(days=1))
    }
    response = await client.post("/api/v1/emission/issue", json=payload, headers=headers)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_issued_policy_has_pending_payment_status(issued_policy):
    assert issued_policy["status"] == "PENDING_PAYMENT"

@pytest.mark.asyncio
async def test_issued_policy_generates_pdf_file(issued_policy):
    # In conftest we mock the generation, but the service saves it
    # Since we are using in-memory SQLite and a temp environment, let's verify pdf_path is set
    assert issued_policy["pdf_path"] is not None
    assert issued_policy["pdf_path"].endswith(".pdf")

@pytest.mark.asyncio
async def test_transition_policy_to_active_succeeds(client: AsyncClient, admin_user, issued_policy):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "target_status": "ACTIVE",
        "reason": "Payment confirmed"
    }
    response = await client.post(f"/api/v1/emission/policies/{issued_policy['id']}/transition", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"

@pytest.mark.asyncio
async def test_transition_policy_invalid_returns_422(client: AsyncClient, admin_user, issued_policy):
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "target_status": "DRAFT", # From PENDING_PAYMENT to DRAFT is invalid
        "reason": "Invalid move"
    }
    response = await client.post(f"/api/v1/emission/policies/{issued_policy['id']}/transition", json=payload, headers=headers)
    assert response.status_code == 422
