import asyncio
import google.generativeai as genai
from app.core.config import settings


async def test_gemini_direct():
    print(
        f"🔍 Verificando API Key: {settings.GOOGLE_API_KEY[:5]}...{settings.GOOGLE_API_KEY[-4:]}"
    )

    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        print("📡 Enviando mensaje a Gemini...")
        response = await model.generate_content_async(
            "Hola, ¿funcionas? Responde de forma muy breve."
        )

        print(
            f"\n✅ Respuesta real de la API:\n{'-' * 40}\n{response.text.strip()}\n{'-' * 40}"
        )
    except Exception as e:
        print(f"❌ Error al conectar con Google Gemini: {e}")


if __name__ == "__main__":
    asyncio.run(test_gemini_direct())
