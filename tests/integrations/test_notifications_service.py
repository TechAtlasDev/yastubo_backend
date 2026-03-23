from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_on_policy_issued_calls_email_and_whatsapp(notifications_service):
    policy = SimpleNamespace(policy_number="YAS-1")
    client = SimpleNamespace(first_name="Ana")

    notifications_service.email.send_policy_confirmation = AsyncMock(return_value=True)
    notifications_service.whatsapp.send_policy_confirmation_wa = AsyncMock(return_value=True)

    await notifications_service.on_policy_issued(policy, client, b"pdf")

    notifications_service.email.send_policy_confirmation.assert_awaited_once()
    notifications_service.whatsapp.send_policy_confirmation_wa.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_payment_failed_twice_sends_whatsapp_reminder(notifications_service):
    policy = SimpleNamespace(policy_number="YAS-2")
    client = SimpleNamespace(first_name="Ana")

    notifications_service.email.send_payment_failed = AsyncMock(return_value=True)
    notifications_service.whatsapp.send_payment_reminder_wa = AsyncMock(return_value=True)

    await notifications_service.on_payment_failed(policy, client, attempt=2)

    notifications_service.email.send_payment_failed.assert_awaited_once_with(policy, client, 2)
    notifications_service.whatsapp.send_payment_reminder_wa.assert_awaited_once_with(policy, client)
