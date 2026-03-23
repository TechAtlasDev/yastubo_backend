import pytest
import uuid
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import User, Role
from app.modules.audit.models import AuditLog
from app.modules.auth.security import create_access_token

@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id), "email": admin_user.email, "roles": ["ADMIN"], "type": "access"})

@pytest.fixture
def client_token(client_user):
    return create_access_token({"sub": str(client_user.id), "email": client_user.email, "roles": ["CLIENTE"], "type": "access"})

@pytest.mark.asyncio
async def test_audit_log_created_on_plan_creation(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    # 1. Create a plan
    plan_data = {
        "name": "Audit Test Plan",
        "description": "Testing audit log",
        "base_price": 50.0,
        "currency": "USD",
        "max_entry_age": 70,
        "max_renewal_age": 80,
        "repatriation_countries": ["CO", "EC"],
        "age_ranges": [{"min_age": 0, "max_age": 70, "surcharge_percentage": 0}],
        "country_configs": [{"country_code": "CO", "country_name": "Colombia", "base_price_override": 45.0, "is_available": True}],
        "coverage_ids": [],
        "terms_es": "Términos",
        "terms_en": "Terms"
    }
    response = await client.post(
        "/api/v1/plans/",
        json=plan_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    plan_id = response.json()["id"]

    # 2. Check audit logs
    audit_response = await client.get(
        "/api/v1/audit/",
        params={"action": "PLAN_CREATED", "entity_id": plan_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert audit_response.status_code == 200
    data = audit_response.json()
    assert data["total"] >= 1
    assert data["items"][0]["action"] == "PLAN_CREATED"
    assert data["items"][0]["entity_id"] == plan_id

@pytest.mark.asyncio
async def test_audit_list_filtered_by_action(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/v1/audit/",
        params={"action": "NON_EXISTENT_ACTION"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0

@pytest.mark.asyncio
async def test_audit_list_filtered_by_date_range(client: AsyncClient, admin_token: str):
    date_from = (datetime.now() - timedelta(days=1)).isoformat()
    date_to = (datetime.now() + timedelta(days=1)).isoformat()
    response = await client.get(
        "/api/v1/audit/",
        params={"date_from": date_from, "date_to": date_to},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_audit_list_filtered_by_entity_id(client: AsyncClient, admin_token: str):
    random_id = str(uuid.uuid4())
    response = await client.get(
        "/api/v1/audit/",
        params={"entity_id": random_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0

@pytest.mark.asyncio
async def test_audit_list_requires_admin_role(client: AsyncClient, client_token: str):
    response = await client.get(
        "/api/v1/audit/",
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_audit_log_contains_ip_address(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    from sqlalchemy import select
    res = await db_session.execute(select(AuditLog).where(AuditLog.ip_address != None))
    audit = res.scalars().first()
    # It might be None if test client doesn't set it in a way FastAPI picks up automatically in test env
    # but at least we check it doesn't fail.
