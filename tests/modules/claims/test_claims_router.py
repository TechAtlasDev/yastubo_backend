import pytest
from httpx import AsyncClient
from app.modules.auth.security import create_access_token
from app.modules.claims.state_machine import ClaimStatus
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_claims_router_flow(client: AsyncClient, admin_user, issued_policy):
    # Setup Auth
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    policy_id = issued_policy["id"]
    beneficiary_id = issued_policy["beneficiaries"][0]["id"]

    # 1. Create Claim
    claim_payload = {
        "policy_id": policy_id,
        "beneficiary_id": beneficiary_id,
        "description": "API Test Claim",
    }

    with patch(
        "app.modules.claims.service.redis_client.publish", new_callable=AsyncMock
    ):
        response = await client.post(
            "/api/v1/claims/", json=claim_payload, headers=headers
        )

    assert response.status_code == 201
    claim = response.json()
    assert claim["status"] == "REPORTED"
    claim_id = claim["id"]

    # 2. Get Claim
    response = await client.get(f"/api/v1/claims/{claim_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == claim_id

    # 3. Add Expense
    expense_payload = {"amount": 200.50, "currency": "USD", "expense_type": "MEDICAL"}
    response = await client.post(
        f"/api/v1/claims/{claim_id}/expenses", json=expense_payload, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 200.50

    # 4. Update Status (Transition to IN_REVIEW)
    status_payload = {"status": ClaimStatus.IN_REVIEW}
    response = await client.patch(
        f"/api/v1/claims/{claim_id}/status", json=status_payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "IN_REVIEW"

    # 5. Approve Claim (Should trigger background job)
    status_payload = {"status": ClaimStatus.APPROVED}
    with patch("arq.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_arq = AsyncMock()
        mock_create_pool.return_value = mock_arq

        response = await client.patch(
            f"/api/v1/claims/{claim_id}/status", json=status_payload, headers=headers
        )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    mock_create_pool.assert_called_once()


@pytest.mark.asyncio
async def test_claims_invalid_transition(
    client: AsyncClient, admin_user, issued_policy
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Create claim
    claim_payload = {
        "policy_id": issued_policy["id"],
        "beneficiary_id": issued_policy["beneficiaries"][0]["id"],
        "description": "Invalid transition test",
    }
    with patch(
        "app.modules.claims.service.redis_client.publish", new_callable=AsyncMock
    ):
        response = await client.post(
            "/api/v1/claims/", json=claim_payload, headers=headers
        )

    claim_id = response.json()["id"]

    # Try invalid transition: REPORTED -> PAID (must go through APPROVED)
    status_payload = {"status": ClaimStatus.PAID}
    response = await client.patch(
        f"/api/v1/claims/{claim_id}/status", json=status_payload, headers=headers
    )

    assert response.status_code == 400
    assert "Invalid transition" in response.json()["detail"]
