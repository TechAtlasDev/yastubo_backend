import pytest
import uuid
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.emission.state_machine import PolicyStatus
from app.modules.payments.models import PaymentMethod
from app.modules.emission.models import Policy
from app.modules.auth.models import User, Role, UserRole
from app.modules.auth.security import create_access_token

@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id), "email": admin_user.email, "roles": ["ADMIN"], "type": "access"})

@pytest.mark.asyncio
async def test_client_can_see_own_policies(client: AsyncClient, client_user_token: str, active_policy_for_client: Policy):
    response = await client.get(
        "/api/v1/portal/policies",
        headers={"Authorization": f"Bearer {client_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == str(active_policy_for_client.id)

@pytest.mark.asyncio
async def test_client_cannot_see_other_client_policies(client: AsyncClient, admin_token: str, client_user_token: str, db_session: AsyncSession):
    # This test checks if a client can see a policy they don't own
    policy_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/v1/portal/policies/{policy_id}",
        headers={"Authorization": f"Bearer {client_user_token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_client_can_cancel_active_policy(client: AsyncClient, client_user_token: str, active_policy_for_client: Policy):
    response = await client.post(
        f"/api/v1/portal/policies/{active_policy_for_client.id}/cancel",
        json={"reason": "Moving abroad"},
        headers={"Authorization": f"Bearer {client_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == PolicyStatus.CANCELLED

@pytest.mark.asyncio
async def test_client_cannot_cancel_closed_case_policy(client: AsyncClient, client_user_token: str, db_session: AsyncSession, active_policy_for_client: Policy):
    # 1. Set policy to CASE_CLOSED
    active_policy_for_client.status = PolicyStatus.CASE_CLOSED
    await db_session.commit()
    
    response = await client.post(
        f"/api/v1/portal/policies/{active_policy_for_client.id}/cancel",
        json={"reason": "Test"},
        headers={"Authorization": f"Bearer {client_user_token}"}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
@patch("app.modules.portal.service.StripeClient")
async def test_client_can_add_payment_method(mock_stripe, client: AsyncClient, client_user_token: str):
    mock_stripe_instance = AsyncMock()
    mock_stripe_instance.get_payment_method.return_value = {
        "id": "pm_123",
        "card": {"brand": "visa", "last4": "4242", "exp_month": 12, "exp_year": 2025}
    }
    
    with patch("app.modules.payments.stripe_client.StripeClient", return_value=mock_stripe_instance):
        response = await client.post(
            "/api/v1/portal/payment-methods",
            json={"stripe_payment_method_id": "pm_123"},
            headers={"Authorization": f"Bearer {client_user_token}"}
        )
    
    assert response.status_code == 200
    assert response.json()["card_last4"] == "4242"

@pytest.mark.asyncio
async def test_client_can_set_default_payment_method(client: AsyncClient, client_user_token: str, client_user_with_profile, db_session: AsyncSession):
    user, _ = client_user_with_profile
    # 1. Add 2 PMs
    pm1 = PaymentMethod(user_id=user.id, stripe_payment_method_id="pm_1", card_brand="visa", card_last4="1111", card_exp_month=1, card_exp_year=2030, is_default=True)
    pm2 = PaymentMethod(user_id=user.id, stripe_payment_method_id="pm_2", card_brand="mastercard", card_last4="2222", card_exp_month=2, card_exp_year=2030, is_default=False)
    db_session.add_all([pm1, pm2])
    await db_session.commit()
    
    response = await client.put(
        f"/api/v1/portal/payment-methods/{pm2.id}/default",
        headers={"Authorization": f"Bearer {client_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_default"] == True

@pytest.mark.asyncio
@patch("app.modules.portal.service.StripeClient")
async def test_client_can_pay_pending_policy(mock_stripe, client: AsyncClient, client_user_token: str, db_session: AsyncSession, active_policy_for_client: Policy, client_user_with_profile):
    user, _ = client_user_with_profile
    # 1. Set policy to PENDING_PAYMENT
    active_policy_for_client.status = PolicyStatus.PENDING_PAYMENT
    # 2. Add default PM
    pm = PaymentMethod(user_id=user.id, stripe_payment_method_id="pm_123", card_brand="visa", card_last4="4242", card_exp_month=1, card_exp_year=2030, is_default=True)
    db_session.add(pm)
    await db_session.commit()
    
    mock_stripe_instance = AsyncMock()
    mock_stripe_instance.get_customer_id_by_email.return_value = "cus_123"
    mock_stripe_instance.create_payment_intent.return_value = {"id": "pi_123", "status": "succeeded"}
    
    with patch("app.modules.portal.service.StripeClient", return_value=mock_stripe_instance):
        response = await client.post(
            f"/api/v1/portal/policies/{active_policy_for_client.id}/pay",
            headers={"Authorization": f"Bearer {client_user_token}"}
        )
    
    assert response.status_code == 200
    
    # Check DB directly
    from sqlalchemy import select
    from app.modules.payments.models import Transaction
    res = await db_session.execute(select(Transaction).where(Transaction.policy_id == active_policy_for_client.id))
    tx = res.scalar_one()
    assert tx.status == "SUCCEEDED"

@pytest.mark.asyncio
async def test_client_without_profile_returns_404(client: AsyncClient, db_session: AsyncSession, roles):
    # 1. Create a user without a client profile
    email = f"no_profile_{uuid.uuid4().hex[:6]}@example.com"
    user = User(email=email, hashed_password="hashed", full_name="No Profile", is_active=True)
    db_session.add(user)
    await db_session.flush()
    
    # Assign CLIENTE role
    user_role = UserRole(user_id=user.id, role_id=roles["CLIENTE"].id)
    db_session.add(user_role)
    await db_session.commit()
    
    token = create_access_token({"sub": str(user.id), "email": email, "roles": ["CLIENTE"], "type": "access"})
    
    response = await client.get(
        "/api/v1/portal/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
