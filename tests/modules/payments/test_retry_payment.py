import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.modules.auth.security import create_access_token


@pytest.mark.asyncio
async def test_retry_payment_endpoint_success(
    client: AsyncClient, admin_user, db_session, issued_policy
):
    workspace_id = admin_user.workspaces[0].id
    # 1. Setup a failed transaction
    from app.modules.payments.models import Transaction

    transaction = Transaction(
        workspace_id=workspace_id,
        policy_id=issued_policy["id"],
        stripe_payment_intent_id="pi_failed_123",
        amount=float(issued_policy["final_price"]),
        currency=issued_policy["currency"],
        status="FAILED",
        payment_type="ONE_TIME",
        attempt_count=1,
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.modules.payments.service.retry_payment", new_callable=AsyncMock
    ) as mock_retry:
        transaction.client_secret = "pi_123_secret_xyz"
        mock_retry.return_value = transaction

        response = await client.post(
            f"/api/v1/payments/transactions/{transaction.id}/retry", headers=headers
        )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["id"] == str(transaction.id)
    assert res_data["client_secret"] == "pi_123_secret_xyz"


@pytest.mark.asyncio
async def test_retry_payment_already_succeeded_fails(
    client: AsyncClient, admin_user, db_session, issued_policy
):
    workspace_id = admin_user.workspaces[0].id
    # 1. Setup a succeeded transaction
    from app.modules.payments.models import Transaction

    transaction = Transaction(
        workspace_id=workspace_id,
        policy_id=issued_policy["id"],
        stripe_payment_intent_id="pi_success_123",
        amount=float(issued_policy["final_price"]),
        currency=issued_policy["currency"],
        status="SUCCEEDED",
        payment_type="ONE_TIME",
    )
    db_session.add(transaction)
    await db_session.commit()

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/payments/transactions/{transaction.id}/retry", headers=headers
    )

    assert response.status_code == 400
    assert "already succeeded" in response.json()["detail"]
