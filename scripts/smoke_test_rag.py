import asyncio
import io
import uuid
from httpx import AsyncClient, ASGITransport
from reportlab.pdfgen import canvas
from app.main import app
from app.modules.auth.security import create_access_token
from sqlalchemy import select
from app.core.database import SessionLocal
from app.modules.auth.models import User
from app.modules.organizations.models import Company


async def smoke_test_rag():
    print("🚀 Iniciando Smoke Test de RAG Real...")

    # 1. Obtener un usuario admin y su compañía para el test
    async with SessionLocal() as db:
        result = await db.execute(select(User).limit(1))
        admin_user = result.scalar_one_or_none()
        comp_result = await db.execute(select(Company).limit(1))
        company = comp_result.scalar_one_or_none()

    if not admin_user or not company:
        print(
            "❌ Error: No se encontró un usuario o compañía en la base de datos para la prueba."
        )
        return

    token = create_access_token(data={"sub": str(admin_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    session_id = f"test-session-{uuid.uuid4().hex[:8]}"

    # 2. Crear un PDF con información "secreta" para validar el RAG
    print("📄 Generando PDF de prueba...")
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    fact_secret = f"CODIGO_SECRETO_YASTUBO: {uuid.uuid4().hex[:12]}"
    c.drawString(100, 750, "DOCUMENTO DE CONFIDENCIALIDAD YASTUBO V1")
    c.drawString(
        100, 730, f"El beneficio exclusivo para clientes premium es: {fact_secret}"
    )
    c.drawString(
        100, 710, "Este beneficio cubre un 50% de descuento en renovaciones anuales."
    )
    c.save()
    pdf_buffer.seek(0)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 3. Subir el PDF (Prueba de Embeddings Reales de Google)
        print("⬆️ Subiendo PDF al RAG (Generando embeddings reales con Gemini)...")
        files = {"file": ("manual_secreto.pdf", pdf_buffer, "application/pdf")}
        upload_res = await client.post(
            "/api/v1/ai/knowledge/upload", headers=headers, files=files
        )

        if upload_res.status_code != 200:
            print(f"❌ Fallo en la subida: {upload_res.text}")
            return
        print("✅ PDF procesado y vectorizado con éxito.")

        # 4. Preguntar al Chat (Prueba de Retrieval + Generación Real)
        print("💬 Preguntando a la IA sobre el contenido del PDF...")
        chat_payload = {
            "session_id": session_id,
            "message": "¿Cuál es el código secreto de Yastubo y qué beneficio tiene?",
        }
        chat_res = await client.post(
            "/api/v1/ai/chat", headers=headers, json=chat_payload
        )

        if chat_res.status_code == 200:
            answer = chat_res.json()["response"]
            print(f"\n🤖 Respuesta de la IA:\n{'-' * 40}\n{answer}\n{'-' * 40}")

            if fact_secret.split(": ")[1] in answer:
                print(
                    "\n✨ ¡ÉXITO TOTAL! La IA encontró el dato en el PDF y respondió correctamente."
                )
            else:
                print(
                    "\n⚠️ La IA respondió, pero no parece haber encontrado el dato exacto del PDF."
                )
        else:
            print(f"❌ Error en el chat: {chat_res.text}")


if __name__ == "__main__":
    asyncio.run(smoke_test_rag())
