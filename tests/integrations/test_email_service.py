from types import SimpleNamespace

import pytest

from app.modules.notifications.email_service import EmailService


@pytest.mark.asyncio
async def test_email_sends_when_enabled(mock_httpx):
    mock_httpx.enqueue(mock_httpx.response(status_code=202))
    service = EmailService("key", "from@yastubo.com", "Yastubo", enabled=True)

    ok = await service.send(
        to_email="test@example.com",
        to_name="Test",
        subject="Subject",
        html_content="<b>Hi</b>",
    )

    assert ok is True
    assert len(mock_httpx.calls) == 1


@pytest.mark.asyncio
async def test_email_skips_when_disabled_and_returns_true(mock_httpx):
    service = EmailService("", "from@yastubo.com", "Yastubo", enabled=False)
    ok = await service.send("test@example.com", "Test", "Subject", "<b>Hi</b>")

    assert ok is True
    assert len(mock_httpx.calls) == 0


@pytest.mark.asyncio
async def test_email_policy_confirmation_attaches_pdf(mock_httpx):
    mock_httpx.enqueue(mock_httpx.response(status_code=202))
    service = EmailService("key", "from@yastubo.com", "Yastubo", enabled=True)

    policy = SimpleNamespace(
        policy_number="YAS-2026-000001",
        plan_version_snapshot={"name": "Plan Familiar"},
        currency="USD",
        final_price=50.0,
    )
    client = SimpleNamespace(
        first_name="Ana", last_name="Pérez", email="ana@example.com"
    )

    ok = await service.send_policy_confirmation(policy, client, pdf_bytes=b"pdf-data")

    assert ok is True
    method, url, kwargs = mock_httpx.calls[0]
    assert method == "POST"
    attachments = kwargs["json"]["attachments"]
    assert len(attachments) == 1
    assert attachments[0]["filename"].endswith(".pdf")


@pytest.mark.asyncio
async def test_email_returns_false_on_sendgrid_error(mock_httpx):
    mock_httpx.enqueue(mock_httpx.response(status_code=500))
    service = EmailService("key", "from@yastubo.com", "Yastubo", enabled=True)

    ok = await service.send("test@example.com", "Test", "Subject", "<b>Hi</b>")

    assert ok is False
