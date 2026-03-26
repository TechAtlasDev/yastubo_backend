import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.security import create_access_token
from app.modules.auth.models import User, Role
from app.modules.workspaces.models import Workspace, UserWorkspace
from sqlalchemy import select
from unittest.mock import patch, AsyncMock

@pytest.fixture
async def reseller_user(db_session, roles):
    user = User(
        email="reseller@yastubo.com",
        hashed_password="hash",
        full_name="Reseller User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # Add VENDEDOR role
    from app.modules.auth.models import UserRole
    user_role = UserRole(user_id=user.id, role_id=roles["VENDEDOR"].id)
    db_session.add(user_role)
    
    # Create Workspace for this reseller
    workspace = Workspace(
        name="Reseller Agency",
        slug="reseller-agency",
        is_reseller=True,
        stripe_connect_id="acct_mock_123",
        commission_rate=10.0 # Platform takes 10%
    )
    db_session.add(workspace)
    await db_session.flush()
    
    # Link User to Workspace
    user_ws = UserWorkspace(user_id=user.id, workspace_id=workspace.id, is_owner=True)
    db_session.add(user_ws)
    
    await db_session.commit()
    await db_session.refresh(user, ["roles", "workspaces"])
    return user, workspace

@pytest.mark.asyncio
async def test_multi_tenancy_and_reseller_flow(client: AsyncClient, reseller_user, db_session):
    user, workspace = reseller_user
    token = create_access_token({"sub": str(user.id), "roles": ["VENDEDOR"], "type": "access"})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": str(workspace.id)
    }

    # 1. Test Reseller Dashboard (Phase 2)
    response = await client.get("/api/v1/payments/reseller/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_sales_count"] == 0
    assert float(data["total_commissions_earned"]) == 0.0

    # 2. Test AI Chat with RAG (Phase 3) - Mocked
    chat_payload = {"session_id": "session-123", "message": "Hola, ¿qué planes tienen?"}
    
    with patch("app.modules.ai.service.AIService.chat_with_context", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "Respuesta simulada de Gemini basada en contexto."
        
        response = await client.post("/api/v1/ai/chat", json=chat_payload, headers=headers)
        assert response.status_code == 200
        assert response.json()["response"] == "Respuesta simulada de Gemini basada en contexto."
        mock_chat.assert_called_once()

    # 3. Test Passbook Generation (Phase 5) - Mocked
    # We need a policy for this. Let's create one quickly in this workspace.
    from app.modules.emission.models import Policy, Client as DBClient
    from datetime import date
    
    test_client = DBClient(
        workspace_id=workspace.id,
        first_name="Test",
        last_name="Client",
        email="test@client.com",
        birth_date=date(1990, 1, 1),
        nationality="CO",
        country_of_residence="ES",
        document_type="ID",
        document_number="123",
        created_by=user.id
    )
    db_session.add(test_client)
    await db_session.flush()
    
    policy = Policy(
        workspace_id=workspace.id,
        policy_number="POL-TEST-001",
        client_id=test_client.id,
        plan_id=uuid.uuid4(), # Mock plan ID
        plan_version_snapshot={"name": "Plan Mock"},
        status="ACTIVE",
        base_price=100.0,
        surcharge_amount=0.0,
        final_price=100.0,
        country_code="ES",
        issued_by=user.id
    )
    db_session.add(policy)
    await db_session.commit()

    # Request Passbook
    with patch("app.modules.emission.passbook_service.PassbookService.generate_policy_pass", new_callable=AsyncMock) as mock_pass:
        mock_pass.return_value = b"MOCK_PKPASS_CONTENT"
        
        response = await client.get(f"/api/v1/emission/policies/{policy.id}/passbook", headers=headers)
        assert response.status_code == 200
        assert response.content == b"MOCK_PKPASS_CONTENT"
        assert response.headers["content-type"] == "application/vnd.apple.pkpass"

@pytest.mark.asyncio
async def test_multi_tenancy_security(client: AsyncClient, admin_user, reseller_user):
    # User from Workspace A should not access Data from Workspace B
    _, workspace = reseller_user # Workspace A
    
    # Admin User (not in Workspace A by default in this test)
    token = create_access_token({"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"})
    
    # Try to access Reseller A dashboard with Admin token but without being in that workspace
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": str(workspace.id)
    }
    
    response = await client.get("/api/v1/payments/reseller/dashboard", headers=headers)
    # Should be 403 Forbidden because admin_user is not linked to workspace A
    assert response.status_code == 403
    assert "You do not have access to this workspace" in response.json()["detail"]
