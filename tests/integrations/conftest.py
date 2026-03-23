from collections import deque
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from app.modules.notifications.email_service import EmailService
from app.modules.notifications.whatsapp_service import WhatsAppService
from app.modules.notifications.service import NotificationsService


@dataclass
class MockHTTPXResponse:
    status_code: int = 200
    json_data: dict | None = None

    def json(self):
        return self.json_data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class MockHTTPXClient:
    responses = deque()
    calls = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return self.responses.popleft() if self.responses else MockHTTPXResponse()

    async def patch(self, url, **kwargs):
        self.calls.append(("PATCH", url, kwargs))
        return self.responses.popleft() if self.responses else MockHTTPXResponse()


@pytest.fixture
def mock_httpx(monkeypatch):
    import httpx

    MockHTTPXClient.responses.clear()
    MockHTTPXClient.calls.clear()
    monkeypatch.setattr(httpx, "AsyncClient", MockHTTPXClient)

    def enqueue(*responses: MockHTTPXResponse):
        for response in responses:
            MockHTTPXClient.responses.append(response)

    return SimpleNamespace(
        enqueue=enqueue,
        calls=MockHTTPXClient.calls,
        response=MockHTTPXResponse,
    )


@pytest.fixture
def notifications_service():
    email = EmailService(
        api_key="",
        from_email="noreply@yastubo.com",
        from_name="Yastubo",
        enabled=False,
    )
    whatsapp = WhatsAppService(
        account_sid="",
        auth_token="",
        from_number="whatsapp:+14155238886",
        enabled=False,
    )
    return NotificationsService(email=email, whatsapp=whatsapp)
