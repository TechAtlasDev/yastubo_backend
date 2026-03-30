import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_incoming_call_returns_twiml(client: AsyncClient):
    response = await client.post("/api/v1/voice/incoming-call")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    content = response.text
    assert "<Response>" in content
    assert "<Stream" in content
    assert "voice/stream" in content
