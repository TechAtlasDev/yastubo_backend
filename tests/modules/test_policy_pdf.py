import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.security import create_access_token


@pytest.mark.asyncio
async def test_download_policy_pdf_success(
    client: AsyncClient, admin_user, issued_policy
):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    policy_id = issued_policy["id"]

    response = await client.get(
        f"/api/v1/emission/policies/{policy_id}/pdf", headers=headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_download_policy_pdf_not_found(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    random_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/v1/emission/policies/{random_id}/pdf", headers=headers
    )

    assert response.status_code == 404
