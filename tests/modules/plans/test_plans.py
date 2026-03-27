import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.security import create_access_token


# CRUD
@pytest.mark.asyncio
async def test_create_plan_as_admin_returns_201(
    client: AsyncClient, admin_user, plan_payload
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/api/v1/plans/", json=plan_payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == plan_payload["name"]


@pytest.mark.asyncio
async def test_create_plan_as_vendedor_returns_403(
    client: AsyncClient, db_session, roles, plan_payload
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
    response = await client.post("/api/v1/plans/", json=plan_payload, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_plans_returns_only_active_by_default(
    client: AsyncClient, client_user, created_plan, admin_user
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Active should return 1
    res = await client.get("/api/v1/plans/", headers=headers)
    assert len(res.json()) == 1

    # 2. Toggle to inactive
    admin_token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    await client.patch(
        f"/api/v1/plans/{created_plan['id']}/toggle",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 3. Active only should return 0
    res = await client.get("/api/v1/plans/", headers=headers)
    assert len(res.json()) == 0


@pytest.mark.asyncio
async def test_get_plan_by_id_returns_full_detail(
    client: AsyncClient, client_user, created_plan
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/plans/{created_plan['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["age_ranges"]) == 2
    assert len(data["country_configs"]) == 2
    assert len(data["coverages"]) == 1


@pytest.mark.asyncio
async def test_get_nonexistent_plan_returns_404(client: AsyncClient, client_user):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/plans/{uuid.uuid4()}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_plan_creates_new_version(
    client: AsyncClient, admin_user, created_plan
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {"name": "Plan Familiar V2"}
    response = await client.put(
        f"/api/v1/plans/{created_plan['id']}", json=update_payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Plan Familiar V2"
    assert response.json()["current_version"] == 2


@pytest.mark.asyncio
async def test_toggle_plan_deactivates_and_activates(
    client: AsyncClient, admin_user, created_plan
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Deactivate
    res = await client.patch(
        f"/api/v1/plans/{created_plan['id']}/toggle", headers=headers
    )
    assert res.json()["is_active"] is False

    # Activate
    res = await client.patch(
        f"/api/v1/plans/{created_plan['id']}/toggle", headers=headers
    )
    assert res.json()["is_active"] is True


# Price Endpoint
@pytest.mark.asyncio
async def test_price_endpoint_invalid_country_returns_422(
    client: AsyncClient, client_user, created_plan
):
    token = create_access_token(
        {"sub": str(client_user.id), "roles": ["CLIENTE"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "plan_id": created_plan["id"],
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
    payload = {
        "plan_id": created_plan["id"],
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
