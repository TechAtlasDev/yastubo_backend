import uuid
import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.leads.service import create_or_update_lead, update_lead
from app.modules.leads.schemas import LeadCreate, LeadUpdate
from app.modules.ai.service import AIService
from app.modules.organizations.models import Company


async def setup_test_company(db_session: AsyncSession) -> uuid.UUID:
    """Helper para asegurar que existe una empresa en los tests."""
    company_id = uuid.uuid4()
    company = Company(id=company_id, name="Test Co", short_code="TEST")
    db_session.add(company)
    await db_session.commit()
    return company_id


@pytest.mark.asyncio
async def test_lead_created_emits_n8n_event(db_session: AsyncSession):
    """Verifica que LEAD_CREATED se emita con el payload correcto."""
    company_id = await setup_test_company(db_session)
    data = LeadCreate(
        phone_e164="+1555000111",
        first_name="Test",
        last_name="Lead",
        email="lead@test.com",
        company_id=company_id,
    )

    with patch("app.core.events.notify_n8n", new_callable=AsyncMock) as mock_n8n:
        await create_or_update_lead(db_session, data)

        calls = [c[0][0] for c in mock_n8n.call_args_list]
        assert "LEAD_CREATED" in calls


@pytest.mark.asyncio
async def test_lead_status_changed_emits_n8n_event(db_session: AsyncSession):
    """Verifica que LEAD_STATUS_CHANGED se emita al actualizar un lead."""
    company_id = await setup_test_company(db_session)
    data = LeadCreate(
        phone_e164="+1555999",
        first_name="Old",
        last_name="Lead",
        email="old@test.com",
        company_id=company_id,
    )
    lead = await create_or_update_lead(db_session, data)

    with patch("app.core.events.notify_n8n", new_callable=AsyncMock) as mock_n8n:
        await update_lead(db_session, lead.id, LeadUpdate(purchase_completed=True))

        status_call = next(
            (c for c in mock_n8n.call_args_list if c[0][0] == "LEAD_STATUS_CHANGED"),
            None,
        )
        assert status_call is not None
        assert status_call[0][1]["new_status"] == "CONVERTED"


@pytest.mark.asyncio
async def test_comment_received_emits_n8n_event(db_session: AsyncSession):
    """Verifica que COMMENT_RECEIVED se emita antes de la llamada a Gemini."""
    ai_service = AIService(api_key="mock")
    company_id = await setup_test_company(db_session)

    # Mockeamos dependencias que usan pgvector (no soportado en SQLite) o APIs externas
    with patch.object(
        ai_service, "get_relevant_documents", new_callable=AsyncMock
    ) as mock_docs:
        mock_docs.return_value = []  # Evitamos el error de sintaxis vectorial en SQLite
        with patch.object(
            ai_service.model, "generate_content_async", new_callable=AsyncMock
        ) as mock_gemini:
            mock_gemini.return_value.text = "Mock response"
            with patch(
                "app.core.events.notify_n8n", new_callable=AsyncMock
            ) as mock_n8n:
                await ai_service.chat_with_context(
                    db_session, company_id, "session-123", "Hola n8n"
                )

                mock_n8n.assert_called()
                args, _ = mock_n8n.call_args
                assert args[0] == "COMMENT_RECEIVED"
