import pytest
from datetime import date, timedelta
from unittest.mock import patch, AsyncMock
from app.workers.tasks import send_expiration_reminders
from app.modules.emission.models import Policy
from app.modules.emission.state_machine import PolicyStatus

from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_send_expiration_reminders_picks_correct_policies(
    db_session, issued_policy
):
    from sqlalchemy import select

    # 1. Get policy object from DB and modify to expire in 3 days
    res = await db_session.execute(
        select(Policy).where(Policy.id == issued_policy["id"])
    )
    policy = res.scalar_one()
    policy.status = PolicyStatus.ACTIVE
    policy.end_date = date.today() + timedelta(days=3)
    await db_session.commit()

    # 2. Mock notifications service and SessionLocal
    mock_notif = AsyncMock()

    # Mock for SessionLocal() context manager
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__.return_value = db_session
    mock_session_cm.__aexit__.return_value = None

    with (
        patch("app.workers.tasks.get_notifications_service", return_value=mock_notif),
        patch("app.workers.tasks.SessionLocal", return_value=mock_session_cm),
    ):
        await send_expiration_reminders({})

    # 3. Assert notification was called
    mock_notif.on_payment_reminder.assert_called_once()
    args, _ = mock_notif.on_payment_reminder.call_args
    assert str(args[0].id) == issued_policy["id"]
    assert str(args[1].id) == issued_policy["client_id"]


@pytest.mark.asyncio
async def test_send_expiration_reminders_skips_active_subscription(
    db_session, issued_policy
):
    from sqlalchemy import select

    # 1. Get policy object from DB and modify to expire in 3 days
    res = await db_session.execute(
        select(Policy).where(Policy.id == issued_policy["id"])
    )
    policy = res.scalar_one()
    policy.status = PolicyStatus.ACTIVE
    policy.end_date = date.today() + timedelta(days=3)

    # 2. Add an active subscription
    from app.modules.payments.models import Subscription

    sub = Subscription(
        company_id=policy.company_id,
        policy_id=policy.id,
        stripe_subscription_id="sub_123",
        stripe_customer_id="cus_test_123",
        status="ACTIVE",
        current_period_start=date.today(),
        current_period_end=date.today() + timedelta(days=30),
    )
    db_session.add(sub)
    await db_session.commit()

    # 3. Mock notifications service and SessionLocal
    mock_notif = AsyncMock()

    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__.return_value = db_session
    mock_session_cm.__aexit__.return_value = None

    with (
        patch("app.workers.tasks.get_notifications_service", return_value=mock_notif),
        patch("app.workers.tasks.SessionLocal", return_value=mock_session_cm),
    ):
        await send_expiration_reminders({})

    # 4. Assert notification was NOT called because there's an active subscription
    mock_notif.on_payment_reminder.assert_not_called()
