import pytest
from unittest.mock import AsyncMock, patch
from app.modules.auth.security import create_access_token
from reportlab.pdfgen import canvas
import io


@pytest.mark.asyncio
async def test_upload_pdf_to_rag(client, admin_user, default_company):
    # 1. Crear un token para el usuario admin
    token = create_access_token(data={"sub": str(admin_user.id)})

    # 2. Crear un PDF en memoria
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, "Este es un documento de prueba para el RAG de Yastubo.")
    c.drawString(
        100, 730, "Las polizas cubren accidentes de transito y desastres naturales."
    )
    c.save()
    pdf_buffer.seek(0)

    # 3. Aplicar mock al AIService.generate_embedding
    with patch(
        "app.modules.ai.service.AIService.generate_embedding", new_callable=AsyncMock
    ) as mock_embed:
        mock_embed.return_value = [0.1] * 3072

        files = {"file": ("test_policy.pdf", pdf_buffer, "application/pdf")}
        response = await client.post(
            "/api/v1/ai/knowledge/upload",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
        )

    # 4. Validar la respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "test_policy.pdf"
    assert "polizas cubren" in data["content"]
    assert data["company_id"] == str(default_company.id)
    # Verificamos que se llamó al mock de embedding
    assert mock_embed.called
