import pytest
from unittest.mock import AsyncMock, patch
from app.modules.payments.stripe_client import StripeClient, get_stripe_client
from app.modules.emission.state_machine import PolicyStatus

@pytest.fixture
def mock_stripe():
    stripe = AsyncMock(spec=StripeClient)
    
    # Defaults
    stripe.create_customer.return_value = {"id": "cus_123"}
    stripe.create_payment_intent.return_value = {
        "id": "pi_123", 
        "client_secret": "pi_123_secret",
        "metadata": {"policy_id": "some_id"}
    }
    stripe.create_subscription.return_value = {
        "id": "sub_123",
        "status": "active",
        "current_period_start": 1700000000,
        "current_period_end": 1731536000,
        "latest_invoice": {
            "id": "in_123",
            "payment_intent": {"id": "pi_456"}
        }
    }
    stripe.cancel_subscription.return_value = {
        "id": "sub_123",
        "status": "canceled",
        "cancel_at_period_end": False
    }
    stripe.create_connect_account.return_value = {"id": "acct_123"}
    stripe.create_account_link.return_value = {"url": "https://stripe.com/onboarding"}
    stripe.construct_webhook_event.side_effect = lambda payload, sig, secret: {"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}}
    
    return stripe

@pytest.fixture
async def pending_policy(client, admin_user, issued_policy, db_session):
    # The issued_policy fixture already creates a policy in PENDING_PAYMENT
    # because of auto-transition in service.
    return issued_policy

@pytest.fixture(autouse=True)
def override_stripe_client(app, mock_stripe):
    app.dependency_overrides[get_stripe_client] = lambda: mock_stripe
    yield
    app.dependency_overrides.pop(get_stripe_client, None)
