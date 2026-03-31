import pytest
from httpx import AsyncClient
from app.modules.auth.security import create_access_token


@pytest.mark.asyncio
async def test_create_company_admin(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": "Test Company",
        "short_code": "TESTCO",
        "phone": "+1234567890",
        "email": "test@company.com",
    }
    response = await client.post(
        "/api/v1/organizations/companies", json=payload, headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["short_code"] == "TESTCO"


@pytest.mark.asyncio
async def test_create_company_non_admin(client: AsyncClient, client_user):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": "Test Company", "short_code": "TESTCO"}
    response = await client.post(
        "/api/v1/organizations/companies", json=payload, headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    # Create one first
    await client.post(
        "/api/v1/organizations/companies",
        json={"name": "Company A", "short_code": "COA"},
        headers=headers,
    )

    response = await client.get("/api/v1/organizations/companies", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_company_detail(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    create_res = await client.post(
        "/api/v1/organizations/companies",
        json={"name": "Company B", "short_code": "COB"},
        headers=headers,
    )
    company_id = create_res.json()["id"]

    response = await client.get(
        f"/api/v1/organizations/companies/{company_id}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Company B"


@pytest.mark.asyncio
async def test_create_business_unit(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    # Create company
    create_co = await client.post(
        "/api/v1/organizations/companies",
        json={"name": "Company C", "short_code": "COC"},
        headers=headers,
    )
    company_id = create_co.json()["id"]

    # Create BU
    bu_payload = {"name": "Main Office", "type": "office"}
    response = await client.post(
        f"/api/v1/organizations/companies/{company_id}/business-units",
        json=bu_payload,
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Main Office"
    assert response.json()["company_id"] == company_id


@pytest.mark.asyncio
async def test_list_business_units(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    # Create company
    create_co = await client.post(
        "/api/v1/organizations/companies",
        json={"name": "Company D", "short_code": "COD"},
        headers=headers,
    )
    company_id = create_co.json()["id"]

    # Create BU
    await client.post(
        f"/api/v1/organizations/companies/{company_id}/business-units",
        json={"name": "BU 1", "type": "agency"},
        headers=headers,
    )

    response = await client.get(
        f"/api/v1/organizations/companies/{company_id}/business-units", headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
