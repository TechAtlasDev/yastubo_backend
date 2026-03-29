import pytest
import uuid
from sqlalchemy import select
from httpx import AsyncClient
from app.modules.emission.state_machine import PolicyStatus


@pytest.mark.asyncio
async def test_webhook_payment_succeeded_transitions_policy_to_active(
    client: AsyncClient, admin_user, pending_policy, db_session, mock_stripe
):
    # 1. Create a transaction first
    from app.modules.payments.models import Transaction

    trans = Transaction(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_payment_intent_id="pi_123",
        amount=50.00,
        currency="USD",
        status="PENDING",
        payment_type="ONE_TIME",
    )
    db_session.add(trans)
    await db_session.commit()

    # 2. Call webhook
    payload = {"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}}
    # Mock signature
    headers = {"stripe-signature": "valid_sig"}

    from unittest.mock import patch

    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        response = await client.post(
            "/api/v1/payments/webhook", json=payload, headers=headers
        )
        assert response.status_code == 200
        # Run the task manually
        if mock_add_task.called:
            task_func = mock_add_task.call_args[0][0]
            await task_func()

    # Check policy status
    from app.modules.emission.models import Policy

    await db_session.rollback()  # Ensure we see fresh data
    res = await db_session.execute(
        select(Policy).where(Policy.id == uuid.UUID(pending_policy["id"]))
    )
    policy = res.scalar_one_or_none()
    assert policy is not None
    assert policy.status == PolicyStatus.ACTIVE


@pytest.mark.asyncio
async def test_webhook_payment_failed_once_keeps_pending_payment_status(
    client: AsyncClient, pending_policy, db_session, mock_stripe
):
    from app.modules.payments.models import Transaction

    trans = Transaction(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_payment_intent_id="pi_fail",
        amount=50.00,
        status="PENDING",
        payment_type="ONE_TIME",
        attempt_count=0,
    )
    db_session.add(trans)
    await db_session.commit()

    mock_stripe.construct_webhook_event.side_effect = lambda p, s, sec: {
        "id": "evt_fail_1",
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_fail",
                "last_payment_error": {"message": "Card declined"},
            }
        },
    }

    from unittest.mock import patch

    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        await client.post(
            "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
        )
        if mock_add_task.called:
            task_func = mock_add_task.call_args[0][0]
            await task_func()

    from app.modules.emission.models import Policy

    await db_session.rollback()
    res = await db_session.execute(
        select(Policy).where(Policy.id == uuid.UUID(pending_policy["id"]))
    )
    policy = res.scalar_one_or_none()
    assert policy is not None
    assert policy.status == PolicyStatus.PENDING_PAYMENT


@pytest.mark.asyncio
async def test_webhook_payment_failed_twice_transitions_to_in_arrears(
    client: AsyncClient, pending_policy, db_session, mock_stripe
):
    from app.modules.payments.models import Transaction

    trans = Transaction(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_payment_intent_id="pi_fail_2",
        amount=50.00,
        status="PENDING",
        payment_type="ONE_TIME",
        attempt_count=1,  # Second attempt
    )
    db_session.add(trans)
    await db_session.commit()

    mock_stripe.construct_webhook_event.side_effect = lambda p, s, sec: {
        "id": "evt_fail_2",
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_fail_2",
                "last_payment_error": {"message": "Hard decline"},
            }
        },
    }

    from unittest.mock import patch

    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        await client.post(
            "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
        )
        if mock_add_task.called:
            task_func = mock_add_task.call_args[0][0]
            await task_func()

    from app.modules.emission.models import Policy

    await db_session.rollback()
    res = await db_session.execute(
        select(Policy).where(Policy.id == uuid.UUID(pending_policy["id"]))
    )
    policy = res.scalar_one_or_none()
    assert policy is not None
    assert policy.status == PolicyStatus.IN_ARREARS


@pytest.mark.asyncio
async def test_webhook_subscription_deleted_cancels_policy(
    client: AsyncClient, pending_policy, db_session, mock_stripe
):
    from app.modules.payments.models import Subscription
    from datetime import datetime

    sub = Subscription(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_subscription_id="sub_del",
        stripe_customer_id="cus_123",
        status="ACTIVE",
        current_period_start=datetime.now(),
        current_period_end=datetime.now(),
    )
    db_session.add(sub)
    await db_session.commit()

    mock_stripe.construct_webhook_event.side_effect = lambda p, s, sec: {
        "id": "evt_sub_del",
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_del"}},
    }

    from unittest.mock import patch

    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        await client.post(
            "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
        )
        if mock_add_task.called:
            task_func = mock_add_task.call_args[0][0]
            await task_func()

    from app.modules.emission.models import Policy

    await db_session.rollback()
    res = await db_session.execute(
        select(Policy).where(Policy.id == uuid.UUID(pending_policy["id"]))
    )
    policy = res.scalar_one_or_none()
    assert policy is not None
    assert policy.status == PolicyStatus.CANCELLED


@pytest.mark.asyncio
async def test_webhook_invalid_signature_returns_400(client: AsyncClient, mock_stripe):
    import stripe

    mock_stripe.construct_webhook_event.side_effect = (
        stripe.error.SignatureVerificationError("Invalid", "sig")
    )

    response = await client.post(
        "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "bad"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_webhook_unknown_event_returns_200_silently(
    client: AsyncClient, mock_stripe
):
    mock_stripe.construct_webhook_event.side_effect = lambda p, s, sec: {
        "id": "evt_unknown",
        "type": "some.other.event",
        "data": {},
    }

    response = await client.post(
        "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_invoice_payment_creates_transaction(
    client: AsyncClient, pending_policy, db_session, mock_stripe
):
    from app.modules.payments.models import Subscription
    from datetime import datetime

    sub = Subscription(
        policy_id=uuid.UUID(pending_policy["id"]),
        stripe_subscription_id="sub_inv",
        stripe_customer_id="cus_123",
        status="ACTIVE",
        current_period_start=datetime.now(),
        current_period_end=datetime.now(),
    )
    db_session.add(sub)
    await db_session.commit()

    mock_stripe.construct_webhook_event.side_effect = lambda p, s, sec: {
        "id": "evt_inv_pay",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "subscription": "sub_inv",
                "payment_intent": "pi_new",
                "id": "in_new",
                "amount_paid": 5000,
                "currency": "usd",
            }
        },
    }

    from unittest.mock import patch

    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        await client.post(
            "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
        )
        if mock_add_task.called:
            task_func = mock_add_task.call_args[0][0]
            await task_func()

    from app.modules.payments.models import Transaction

    await db_session.rollback()
    res = await db_session.execute(
        select(Transaction).where(Transaction.stripe_invoice_id == "in_new")
    )
    trans = res.scalar_one_or_none()
    assert trans is not None
    assert trans.payment_type == "SUBSCRIPTION_CHARGE"


@pytest.mark.asyncio
async def test_webhook_idempotency_prevents_duplicate_processing(
    client: AsyncClient, pending_policy, db_session, mock_stripe
):
    from app.modules.payments.models import Transaction, StripeEvent

    # Setup a transaction
    policy_id = uuid.UUID(pending_policy["id"])
    trans = Transaction(
        policy_id=policy_id,
        stripe_payment_intent_id="pi_idemp",
        amount=50.00,
        status="PENDING",
        payment_type="ONE_TIME",
    )
    db_session.add(trans)
    await db_session.commit()

    # Mock identical event returned twice
    mock_stripe.construct_webhook_event.side_effect = lambda p, s, sec: {
        "id": "evt_duplicate_test",
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": "pi_idemp"}},
    }

    from unittest.mock import patch

    # 1. First call - Should process successfully
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        await client.post(
            "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
        )
        if mock_add_task.called:
            task_func = mock_add_task.call_args[0][0]
            await task_func()

    await db_session.rollback()
    # Verify transaction is SUCCEEDED and StripeEvent recorded
    res_tx = await db_session.execute(
        select(Transaction).where(Transaction.stripe_payment_intent_id == "pi_idemp")
    )
    tx_after_first = res_tx.scalar_one()
    assert tx_after_first.status == "SUCCEEDED"

    res_evt = await db_session.execute(
        select(StripeEvent).where(StripeEvent.event_id == "evt_duplicate_test")
    )
    assert res_evt.scalar_one_or_none() is not None

    # 2. Second call with same event ID - Should skip
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        # Reset mock for log check or just rely on state
        with patch("app.modules.payments.webhook_handler.logger.info") as mock_log:
            await client.post(
                "/api/v1/payments/webhook", json={}, headers={"stripe-signature": "sig"}
            )
            if mock_add_task.called:
                task_func = mock_add_task.call_args[0][0]
                await task_func()

            # Should have found it in DB and logged "already processed"
            mock_log.assert_any_call(
                "Stripe event evt_duplicate_test already processed. Skipping."
            )
