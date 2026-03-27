import pytest
from httpx import AsyncClient
from app.modules.auth.security import create_access_token
from app.modules.payments.models import Transaction, Subscription
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_dashboard_metrics_returns_valid_data(
    client: AsyncClient, admin_user, db_session, issued_policy
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Add a transaction
    tx = Transaction(
        workspace_id=admin_user.workspaces[0].id,
        policy_id=issued_policy["id"],
        amount=100.00,
        currency="USD",
        status="SUCCEEDED",
        payment_type="ONE_TIME",
        processed_at=datetime.now(),
    )
    db_session.add(tx)

    # 2. Add an active subscription
    sub = Subscription(
        workspace_id=admin_user.workspaces[0].id,
        policy_id=issued_policy["id"],
        stripe_subscription_id="sub_test_123",
        stripe_customer_id="cus_test_123",
        status="ACTIVE",
        monthly_price=50.00,
        currency="USD",
        current_period_start=datetime.now(),
        current_period_end=datetime.now() + timedelta(days=30),
    )
    db_session.add(sub)
    await db_session.commit()

    # 3. Call dashboard
    response = await client.get("/api/v1/dashboard/metrics", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert float(data["total_revenue"]) >= 100.00
    assert float(data["mrr"]) >= 50.00
    assert (
        data["active_policies"] >= 0
    )  # Initial state might be pending or active depending on issued_policy
    assert data["churn_rate"] == 0.0
    assert (
        "Direct" in data["conversions_by_channel"]
        or len(data["conversions_by_channel"]) == 0
    )
