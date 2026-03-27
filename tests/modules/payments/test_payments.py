import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.security import create_access_token
from app.modules.emission.state_machine import PolicyStatus


@pytest.mark.asyncio
async def test_create_payment_intent_returns_client_secret(
    client: AsyncClient, admin_user, pending_policy
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"policy_id": pending_policy["id"]}

    response = await client.post(
        "/api/v1/payments/intent", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert "client_secret" in response.json()
    assert response.json()["status"] == "PENDING"


@pytest.mark.asyncio
async def test_create_payment_intent_policy_not_pending_returns_422(
    client: AsyncClient, admin_user, db_session, pending_policy
):
    # Change policy status
    from app.modules.emission.models import Policy

    admin_id = admin_user.id
    await db_session.execute(
        Policy.__table__.update()
        .where(Policy.id == uuid.UUID(pending_policy["id"]))
        .values(status=PolicyStatus.ACTIVE)
    )
    await db_session.commit()
    db_session.expire_all()

    token = create_access_token(
        {"sub": str(admin_id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"policy_id": pending_policy["id"]}

    response = await client.post(
        "/api/v1/payments/intent", json=payload, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_subscription_succeeds(
    client: AsyncClient, admin_user, pending_policy, db_session
):
    # Set stripe_price_id on plan
    from app.modules.plans.models import Plan

    await db_session.execute(
        Plan.__table__.update()
        .where(Plan.id == uuid.UUID(pending_policy["plan_id"]))
        .values(stripe_price_id="price_123")
    )
    await db_session.commit()

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"policy_id": pending_policy["id"], "stripe_payment_method_id": "pm_123"}

    response = await client.post(
        "/api/v1/payments/subscription", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_create_subscription_duplicate_returns_409(
    client: AsyncClient, admin_user, pending_policy, db_session
):
    # First create one
    from app.modules.payments.models import Subscription
    from datetime import datetime

    sub = Subscription(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_subscription_id="sub_abc",
        stripe_customer_id="cus_abc",
        status="ACTIVE",
        current_period_start=datetime.now(),
        current_period_end=datetime.now(),
    )
    db_session.add(sub)
    await db_session.commit()

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"policy_id": pending_policy["id"], "stripe_payment_method_id": "pm_123"}

    response = await client.post(
        "/api/v1/payments/subscription", json=payload, headers=headers
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_cancel_subscription_by_admin_succeeds(
    client: AsyncClient, admin_user, pending_policy, db_session
):
    # Create sub
    from app.modules.payments.models import Subscription
    from datetime import datetime

    sub = Subscription(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_subscription_id="sub_123",
        stripe_customer_id="cus_123",
        status="ACTIVE",
        current_period_start=datetime.now(),
        current_period_end=datetime.now(),
    )
    db_session.add(sub)
    await db_session.commit()

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"policy_id": pending_policy["id"], "cancel_immediately": True}

    response = await client.post(
        "/api/v1/payments/subscription/cancel", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELED"


@pytest.mark.asyncio
async def test_cancel_subscription_by_vendedor_returns_403(
    client: AsyncClient, roles, db_session, pending_policy
):
    # Create vendedor
    from app.modules.auth.models import User, UserRole
    from app.modules.auth.security import get_password_hash

    vendedor = User(
        email="v_pay@yastubo.com",
        hashed_password=get_password_hash("pass"),
        full_name="V",
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
    payload = {"policy_id": pending_policy["id"]}

    response = await client.post(
        "/api/v1/payments/subscription/cancel", json=payload, headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_manual_payment_activates_policy(
    client: AsyncClient, admin_user, pending_policy
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"policy_id": pending_policy["id"], "amount": 50.00, "notes": "Efectivo"}

    response = await client.post(
        "/api/v1/payments/manual", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCEEDED"

    # Check policy is active
    res_p = await client.get(
        f"/api/v1/emission/policies/{pending_policy['id']}", headers=headers
    )
    assert res_p.json()["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_list_transactions_filtered_by_policy(
    client: AsyncClient, admin_user, pending_policy
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Create a transaction
    await client.post(
        "/api/v1/payments/intent",
        json={"policy_id": pending_policy["id"]},
        headers=headers,
    )

    response = await client.get(
        f"/api/v1/payments/transactions?policy_id={pending_policy['id']}",
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_connect_onboarding_returns_url(client: AsyncClient, roles, db_session):
    # Create vendedor
    from app.modules.auth.models import User, UserRole
    from app.modules.auth.security import get_password_hash

    vendedor = User(
        email="v_onboard@yastubo.com",
        hashed_password=get_password_hash("pass"),
        full_name="V",
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

    response = await client.post("/api/v1/payments/connect/onboarding", headers=headers)
    assert response.status_code == 200
    assert "url" in response.json()
    assert "stripe.com" in response.json()["url"]
