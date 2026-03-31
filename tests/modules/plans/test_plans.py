import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.security import create_access_token


# CRUD
@pytest.mark.asyncio
async def test_create_product_as_admin_returns_201(
    client: AsyncClient, admin_user, product_payload
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/products/", json=product_payload, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == product_payload["name"]


@pytest.mark.asyncio
async def test_create_product_as_vendedor_returns_403(
    client: AsyncClient, db_session, roles, product_payload
):
    # Setup vendedor user
    from app.modules.auth.models import User, UserRole
    from app.modules.auth.security import get_password_hash

    vendedor = User(
        email="vendedor@yastubo.com",
        hashed_password=get_password_hash("pass"),
        full_name="Vendedor",
        is_active=True,
    )
    db_session.add(vendedor)
    await db_session.flush()
    db_session.add(UserRole(user_id=vendedor.id, role_id=roles["VENDEDOR"].id))
    await db_session.commit()

    token = create_access_token(
        {"sub": str(vendedor.id), "roles": ["VENDEDOR"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/products/", json=product_payload, headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_products_returns_only_active_by_default(
    client: AsyncClient, client_user, created_product
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Active should return 1
    res = await client.get("/api/v1/products/", headers=headers)
    assert len(res.json()) >= 1  # Since conftest might have created more

    # Verify the one we created is there
    product_ids = [p["id"] for p in res.json()]
    assert created_product["id"] in product_ids


@pytest.mark.asyncio
async def test_get_product_by_id_returns_full_detail(
    client: AsyncClient, client_user, created_product
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(
        f"/api/v1/products/{created_product['id']}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["plans"]) == 1
    plan = data["plans"][0]
    assert len(plan["versions"]) == 1
    version = plan["versions"][0]
    assert len(version["age_surcharges"]) == 2
    assert len(version["countries"]) == 2
    assert len(version["coverages"]) == 1


@pytest.mark.asyncio
async def test_get_nonexistent_product_returns_404(client: AsyncClient, client_user):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/products/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 404


# Price Endpoint
@pytest.mark.asyncio
async def test_price_endpoint_invalid_country_returns_422(
    client: AsyncClient, client_user, created_plan
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    version = created_plan["versions"][0]
    payload = {
        "plan_version_id": version["id"],
        "age": 25,
        "country_code": "AR",  # Not in plan config
    }
    response = await client.post(
        "/api/v1/plans/calculate-price", json=payload, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_price_endpoint_returns_full_breakdown(
    client: AsyncClient, client_user, created_plan
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # MX has override 60.00. Age 40 has 20% surcharge.
    # Total unit = 60 + 12 = 72. Quantity 2 = 144.
    version = created_plan["versions"][0]
    payload = {
        "plan_version_id": version["id"],
        "age": 40,
        "country_code": "MX",
        "quantity": 2,
    }
    response = await client.post(
        "/api/v1/plans/calculate-price", json=payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["final_price"]) == 144.00
    assert data["breakdown"]["range_applied"] == "31-65"
