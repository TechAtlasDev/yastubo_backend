import uuid
import pytest
from unittest.mock import patch, AsyncMock
from app.core.events import notify_n8n


@pytest.mark.asyncio
async def test_n8n_event_payloads():
    """Valida los contratos de los eventos implementados para n8n."""

    events_to_test = [
        (
            "LEAD_CREATED",
            {
                "lead_id": str(uuid.uuid4()),
                "email": "test@lead.com",
                "full_name": "Test Lead",
                "source": "IG",
                "company_id": str(uuid.uuid4()),
            },
        ),
        (
            "LEAD_STATUS_CHANGED",
            {
                "lead_id": str(uuid.uuid4()),
                "old_status": "NEW",
                "new_status": "CONVERTED",
                "company_id": str(uuid.uuid4()),
            },
        ),
        (
            "COMMENT_RECEIVED",
            {
                "conversation_id": str(uuid.uuid4()),
                "message": "Hola n8n",
                "sentiment_hint": None,
                "channel": "WEB_CHAT",
            },
        ),
        (
            "AGENT_HANDOFF_REQUIRED",
            {
                "conversation_id": str(uuid.uuid4()),
                "company_id": str(uuid.uuid4()),
                "reason": "user_requested",
                "last_user_message": "Quiero hablar con un humano",
                "last_bot_response": "Te transfiero...",
                "confidence_score": 0.0,
            },
        ),
        (
            "POLICY_STATUS_CHANGED",
            {
                "policy_id": str(uuid.uuid4()),
                "policy_number": "YAS-2026-001",
                "old_status": "PENDING_PAYMENT",
                "new_status": "ACTIVE",
                "client_id": str(uuid.uuid4()),
            },
        ),
        (
            "CLAIM_OPENED",
            {
                "claim_id": str(uuid.uuid4()),
                "policy_id": str(uuid.uuid4()),
                "client_id": str(uuid.uuid4()),
                "claim_type": "REPATRIATION",
                "description": "Fallecimiento en el exterior",
            },
        ),
        (
            "PAYMENT_RETRY_SCHEDULED",
            {
                "transaction_id": str(uuid.uuid4()),
                "policy_id": str(uuid.uuid4()),
                "attempt_number": 1,
                "scheduled_at": "2026-03-31T20:00:00Z",
                "amount": 50.0,
            },
        ),
    ]

    with patch("app.core.events._send_to_n8n", new_callable=AsyncMock) as mock_send:
        # Mockeamos settings para tener una URL activa
        with patch("app.core.config.settings.N8N_WEBHOOK_URL", "http://mock-n8n.com"):
            for event_name, payload in events_to_test:
                await notify_n8n(event_name, payload)

            # Damos un respiro para que las tareas asíncronas se inicien
            import asyncio

            await asyncio.sleep(0.1)

            assert mock_send.call_count == len(events_to_test)

            # Verificar que el primer evento se envió correctamente
            args, _ = mock_send.call_args_list[0]
            assert args[1] == "LEAD_CREATED"
            assert args[2]["email"] == "test@lead.com"


def test_should_handoff_user_requested():
    """Valida detección por intención explícita del usuario."""
    from app.modules.ai.service import AIService

    svc = AIService.__new__(AIService)
    result, reason = svc._should_handoff(
        "quiero hablar con un agente", "Aquí tienes la información"
    )
    assert result is True
    assert reason == "user_requested"


def test_should_handoff_bot_uncertain():
    """Valida detección por incertidumbre de la respuesta del bot."""
    from app.modules.ai.service import AIService

    svc = AIService.__new__(AIService)
    result, reason = svc._should_handoff(
        "¿cuánto cuesta?", "lo siento, no puedo ayudarte con eso"
    )
    assert result is True
    assert reason == "bot_uncertain"


def test_should_not_handoff():
    """Valida que no se dispare handoff en flujo normal."""
    from app.modules.ai.service import AIService

    svc = AIService.__new__(AIService)
    result, reason = svc._should_handoff(
        "¿cuánto cuesta el plan básico?", "El plan básico cuesta $50 mensuales"
    )
    assert result is False
    assert reason == ""
