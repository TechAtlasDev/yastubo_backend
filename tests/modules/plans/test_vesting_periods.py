import pytest
from httpx import AsyncClient
from app.modules.auth.security import create_access_token


@pytest.mark.asyncio
async def test_product_plan_version_includes_vesting_periods(
    client: AsyncClient, admin_user, product_payload
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create product with custom vesting periods in one version
    custom_payload = product_payload.copy()
    version = custom_payload["plans"][0]["versions"][0]
    version["wtime_accident"] = 5
    version["wtime_preexisting"] = 90
    version["wtime_suicide"] = 730

    response = await client.post(
        "/api/v1/products/", json=custom_payload, headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    created_version = data["plans"][0]["versions"][0]
    assert created_version["wtime_accident"] == 5
    assert created_version["wtime_preexisting"] == 90
    assert created_version["wtime_suicide"] == 730


@pytest.mark.asyncio
async def test_plan_version_default_vesting_periods(
    client: AsyncClient, admin_user, product_payload
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create product with default vesting periods (from product_payload)
    response = await client.post(
        "/api/v1/products/", json=product_payload, headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    created_version = data["plans"][0]["versions"][0]

    # Check values from product_payload in conftest.py
    assert created_version["wtime_accident"] == 0
    assert created_version["wtime_preexisting"] == 180
    assert created_version["wtime_suicide"] == 365
