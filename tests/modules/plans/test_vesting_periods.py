import pytest
from httpx import AsyncClient
from app.modules.auth.security import create_access_token


@pytest.mark.asyncio
async def test_plan_includes_vesting_periods(
    client: AsyncClient, admin_user, plan_payload
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create plan with custom vesting periods
    custom_payload = plan_payload.copy()
    custom_payload["vesting_accidental_days"] = 5
    custom_payload["vesting_natural_days"] = 90
    custom_payload["vesting_suicide_days"] = 730

    response = await client.post("/api/v1/plans/", json=custom_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["vesting_accidental_days"] == 5
    assert data["vesting_natural_days"] == 90
    assert data["vesting_suicide_days"] == 730


@pytest.mark.asyncio
async def test_plan_default_vesting_periods(
    client: AsyncClient, admin_user, plan_payload
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create plan with default (omitted in payload if allowed or using defaults)
    response = await client.post("/api/v1/plans/", json=plan_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    # Check defaults from schema/model
    assert data["vesting_accidental_days"] == 0
    assert data["vesting_natural_days"] == 180
    assert data["vesting_suicide_days"] == 365
