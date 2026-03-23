import pytest

from app.modules.notifications.whatsapp_service import WhatsAppService


@pytest.mark.asyncio
async def test_whatsapp_sends_when_enabled(mock_httpx):
    mock_httpx.enqueue(mock_httpx.response(status_code=201))
    service = WhatsAppService("sid", "token", "whatsapp:+14155238886", enabled=True)

    ok = await service.send_message("+573001112233", "Hola")

    assert ok is True
    assert len(mock_httpx.calls) == 1


@pytest.mark.asyncio
async def test_whatsapp_skips_when_disabled_and_returns_true(mock_httpx):
    service = WhatsAppService("", "", "whatsapp:+14155238886", enabled=False)

    ok = await service.send_message("+573001112233", "Hola")

    assert ok is True
    assert len(mock_httpx.calls) == 0


@pytest.mark.asyncio
async def test_whatsapp_returns_false_on_twilio_error(mock_httpx):
    mock_httpx.enqueue(mock_httpx.response(status_code=500))
    service = WhatsAppService("sid", "token", "whatsapp:+14155238886", enabled=True)

    ok = await service.send_message("+573001112233", "Hola")

    assert ok is False
