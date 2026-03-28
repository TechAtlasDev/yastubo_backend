"""Unit tests for DT-05: N8N_WEBHOOK_URL in Settings and core/events.py behavior."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ---------------------------------------------------------------------------
# DT-05: Settings includes N8N_WEBHOOK_URL
# ---------------------------------------------------------------------------

class TestSettingsN8nWebhookUrl:
    def test_settings_has_n8n_webhook_url_attribute(self):
        from app.core.config import Settings
        # The field must exist on the model
        assert "N8N_WEBHOOK_URL" in Settings.model_fields

    def test_default_value_is_empty_string(self):
        from app.core.config import Settings
        field_info = Settings.model_fields["N8N_WEBHOOK_URL"]
        assert field_info.default == ""

    def test_settings_instance_has_n8n_webhook_url(self):
        """Verify the singleton settings object exposes the attribute directly."""
        from app.core.config import settings
        # getattr must work without fallback (no AttributeError)
        value = settings.N8N_WEBHOOK_URL
        assert isinstance(value, str)

    def test_settings_no_getattr_needed(self):
        """Accessing N8N_WEBHOOK_URL must NOT require getattr fallback."""
        from app.core.config import settings
        # This would raise AttributeError if the field were missing
        _ = settings.N8N_WEBHOOK_URL


# ---------------------------------------------------------------------------
# DT-05: events.py uses settings.N8N_WEBHOOK_URL directly
# ---------------------------------------------------------------------------

class TestDispatchEventBehavior:
    @pytest.mark.asyncio
    async def test_skips_dispatch_when_url_empty(self):
        """When N8N_WEBHOOK_URL is empty, dispatch_event returns False and logs warning."""
        from app.core import events as ev_module

        with patch.object(ev_module.settings, "N8N_WEBHOOK_URL", ""):
            result = await ev_module.dispatch_event("TEST_EVENT", {"foo": "bar"})

        assert result is False

    @pytest.mark.asyncio
    async def test_dispatches_when_url_configured(self):
        """When N8N_WEBHOOK_URL is set, dispatch_event POSTs and returns True."""
        from app.core import events as ev_module

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(ev_module.settings, "N8N_WEBHOOK_URL", "https://n8n.example.com/webhook/test"):
            with patch("app.core.events.httpx.AsyncClient", return_value=mock_client):
                result = await ev_module.dispatch_event("LEAD_CREATED", {"lead_id": "123"})

        assert result is True
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args
        # URL must be the configured webhook URL
        assert "https://n8n.example.com/webhook/test" in call_kwargs[0]

    @pytest.mark.asyncio
    async def test_returns_false_on_http_error(self):
        """When the HTTP call fails, dispatch_event returns False (doesn't raise)."""
        import httpx
        from app.core import events as ev_module

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("connection refused"))

        with patch.object(ev_module.settings, "N8N_WEBHOOK_URL", "https://n8n.example.com/webhook/test"):
            with patch("app.core.events.httpx.AsyncClient", return_value=mock_client):
                result = await ev_module.dispatch_event("LEAD_CREATED", {"lead_id": "123"})

        assert result is False

    def test_events_module_uses_direct_attribute_access(self):
        """events.py source must use settings.N8N_WEBHOOK_URL, not getattr fallback."""
        import inspect
        from app.core import events as ev_module

        source = inspect.getsource(ev_module)
        # Must NOT use getattr(settings, "N8N_WEBHOOK_URL", ...) any more
        assert 'getattr(settings, "N8N_WEBHOOK_URL"' not in source
        # Must use direct access
        assert "settings.N8N_WEBHOOK_URL" in source
