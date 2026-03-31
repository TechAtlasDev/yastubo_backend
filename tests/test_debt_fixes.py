import pytest
import uuid
import asyncio
from datetime import date, datetime
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from app.modules.emission.service import mark_beneficiary_deceased
from app.modules.ai.service import AIService
from app.modules.leads.service import create_or_update_lead
from app.modules.leads.schemas import LeadCreate
from app.modules.emission.models import Beneficiary, Policy
from app.modules.payments.models import Subscription
from app.modules.ai.models import ChatMessage


@pytest.mark.asyncio
async def test_mark_beneficiary_deceased_adjusts_stripe(db_session, default_company):
    # Setup: Policy with Subscription and Beneficiary
    from app.modules.emission.models import Client

    client = Client(
        company_id=default_company.id,
        first_name="Test",
        last_name="Client",
        email="debt@example.com",
        phone="+573001112233",
        birth_date=date(1990, 1, 1),
        nationality="CO",
        country_of_residence="CO",
        document_type="ID",
        document_number="123456",
        created_by=uuid.uuid4(),
    )
    db_session.add(client)
    await db_session.flush()

    policy = Policy(
        company_id=default_company.id,
        policy_number="YAS-DEBT-001",
        client_id=client.id,
        plan_id=uuid.uuid4(),
        plan_version_id=uuid.uuid4(),
        plan_version_snapshot={"name": "Test Plan"},
        status="ACTIVE",
        base_price=100.0,
        surcharge_amount=0.0,
        final_price=100.0,
        currency="USD",
        country_code="CO",
        issued_by=client.created_by,
    )
    db_session.add(policy)
    await db_session.flush()

    sub = Subscription(
        company_id=default_company.id,
        policy_id=policy.id,
        stripe_subscription_id="sub_test_123",
        stripe_customer_id="cus_test_123",
        status="ACTIVE",
        monthly_price=100.0,
        mrr_snapshot=100.0,
        current_period_start=datetime.now(),
        current_period_end=datetime.now(),
    )
    db_session.add(sub)

    beneficiary = Beneficiary(
        policy_id=policy.id,
        first_name="Bene",
        last_name="One",
        date_of_birth=date(1995, 1, 1),
        kinship_type="SPOUSE",
        country_of_residence="CO",
        individual_price=20.0,
        coverage_status="ACTIVE",
    )
    db_session.add(beneficiary)
    await db_session.commit()

    # Mock StripeClient
    mock_stripe = AsyncMock()
    with patch(
        "app.modules.payments.stripe_client.get_stripe_client", return_value=mock_stripe
    ):
        await mark_beneficiary_deceased(db_session, beneficiary.id, "Admin")

        # Verify Stripe was called with correct amount (100 - 20 = 80)
        mock_stripe.update_subscription_item_price.assert_called_once_with(
            subscription_id="sub_test_123", new_amount_cents=8000, currency="usd"
        )

        # Verify DB updates
        await db_session.refresh(beneficiary)
        await db_session.refresh(sub)
        assert beneficiary.deceased_flag is True
        assert beneficiary.billing_adjustment_confirmed is True
        assert sub.monthly_price == 80.0


@pytest.mark.asyncio
async def test_ai_chat_persists_history(db_session, default_company):
    service = AIService(api_key="fake_key")

    # Mock Gemini response
    mock_response = AsyncMock()
    mock_response.text = "Hello! I am your assistant."
    service.model.generate_content_async = AsyncMock(return_value=mock_response)

    # Mock embeddings to avoid network
    service.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    # Mock relevant documents to avoid pgvector/sqlite error
    service.get_relevant_documents = AsyncMock(return_value=[])

    session_id = "session_123"
    message = "What is Yastubo?"

    # First call
    response = await service.chat_with_context(
        db_session, default_company.id, session_id, message
    )
    assert response == "Hello! I am your assistant."

    # Manually update timestamps to ensure order in SQLite
    msgs_stmt = select(ChatMessage).order_by(ChatMessage.id)  # arbitrary but fixed
    msgs = (await db_session.execute(msgs_stmt)).scalars().all()
    for i, m in enumerate(msgs):
        m.created_at = datetime(2026, 3, 29, 10, 0, i)  # 10:00:00, 10:00:01
    await db_session.commit()

    # Second call - should use history
    await service.chat_with_context(
        db_session, default_company.id, session_id, "And who are you?"
    )

    # Verify call to Gemini included history
    # The prompt should contain "What is Yastubo?" and "Hello! I am your assistant."
    call_args = service.model.generate_content_async.call_args[0][0]
    assert "What is Yastubo?" in call_args
    assert "Hello! I am your assistant." in call_args


@pytest.mark.asyncio
async def test_lead_sync_to_zoho_called(db_session, default_company):
    lead_data = LeadCreate(
        first_name="Zoho",
        last_name="Test",
        phone_e164="+573005554433",
        email="zoho@example.com",
        company_id=default_company.id,
    )

    with patch("app.modules.leads.service.sync_lead_to_crm") as mock_sync:
        with patch("app.modules.leads.service.get_zoho_client"):
            # We use create_task, so we might need to wait or mock it to be sync for test
            # In service.py: asyncio.create_task(sync_lead_to_crm(get_zoho_client(), lead))

            # To test this reliably, we can wrap the task or just check the call if it's not too flaky
            await create_or_update_lead(db_session, lead_data)

            # Since it's a task, let's wait a bit or use a different approach
            # Actually, if we mock sync_lead_to_crm, we can check if it was called
            # but create_task might not have finished yet.

            # Let's wait a tiny bit
            await asyncio.sleep(0.1)
            mock_sync.assert_called_once()
