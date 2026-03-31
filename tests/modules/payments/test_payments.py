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


# ── Retry Payment Tests ──────────────────────────────────────────────────────


@pytest.fixture
async def failed_transaction(db_session, pending_policy):
    """Creates a FAILED transaction with attempt_count=1 for retry tests."""
    from app.modules.payments.models import Transaction
    import uuid

    tx = Transaction(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_payment_intent_id="pi_failed_001",
        amount=50.00,
        currency="USD",
        status="FAILED",
        payment_type="ONE_TIME",
        attempt_count=1,
        last_error="Your card was declined.",
    )
    db_session.add(tx)
    await db_session.commit()
    await db_session.refresh(tx)
    return tx


@pytest.mark.asyncio
async def test_retry_payment_succeeds_on_first_retry(
    client: AsyncClient, admin_user, failed_transaction
):
    """First retry: creates new PaymentIntent, increments attempt_count to 2."""
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/payments/transactions/{failed_transaction.id}/retry",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["attempt_count"] == 2
    assert data["status"] == "PENDING"
    assert "client_secret" in data
    assert "2 of 2" in data["message"]


@pytest.mark.asyncio
async def test_retry_payment_blocks_at_max_attempts(
    client: AsyncClient, admin_user, db_session, pending_policy
):
    """At attempt_count >= 2: returns 422 and triggers notification."""
    from app.modules.payments.models import Transaction
    import uuid

    tx = Transaction(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_payment_intent_id="pi_failed_maxed",
        amount=50.00,
        currency="USD",
        status="FAILED",
        payment_type="ONE_TIME",
        attempt_count=2,
        last_error="Card declined again.",
    )
    db_session.add(tx)
    await db_session.commit()
    await db_session.refresh(tx)

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/payments/transactions/{tx.id}/retry",
        headers=headers,
    )
    assert response.status_code == 422
    assert "Maximum retry attempts" in response.json()["detail"]
    assert "notification" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_retry_payment_rejects_non_failed_transaction(
    client: AsyncClient, admin_user, db_session, pending_policy
):
    """Only FAILED transactions can be retried."""
    from app.modules.payments.models import Transaction
    import uuid

    tx = Transaction(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_payment_intent_id="pi_pending_001",
        amount=50.00,
        currency="USD",
        status="PENDING",
        payment_type="ONE_TIME",
        attempt_count=1,
    )
    db_session.add(tx)
    await db_session.commit()
    await db_session.refresh(tx)

    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/payments/transactions/{tx.id}/retry",
        headers=headers,
    )
    assert response.status_code == 422
    assert "FAILED" in response.json()["detail"]


@pytest.mark.asyncio
async def test_retry_payment_returns_404_for_unknown_transaction(
    client: AsyncClient, admin_user
):
    """Unknown transaction ID returns 404."""
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = uuid.uuid4()

    response = await client.post(
        f"/api/v1/payments/transactions/{fake_id}/retry",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_retry_payment_requires_auth(client: AsyncClient, failed_transaction):
    """Unauthenticated request returns 401."""
    response = await client.post(
        f"/api/v1/payments/transactions/{failed_transaction.id}/retry"
    )
    assert response.status_code == 401
