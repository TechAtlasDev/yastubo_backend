import pytest
from unittest.mock import patch, AsyncMock
from app.modules.ai.service import AIService


@pytest.mark.asyncio
async def test_voice_chat_response():
    # 1. Mock Gemini response
    mock_model = AsyncMock()
    mock_response = AsyncMock()
    mock_response.text = (
        "Hola, soy el asistente de voz de Yastubo. ¿En qué puedo ayudarte?"
    )
    mock_model.generate_content_async.return_value = mock_response

    with patch("google.generativeai.GenerativeModel", return_value=mock_model):
        service = AIService(api_key="fake_key")
        response = await service.voice_chat("Hola")

        assert "Yastubo" in response
        mock_model.generate_content_async.assert_called_once()
        # Verify prompt instructions
        args, _ = mock_model.generate_content_async.call_args
        assert "Asistente de voz" in args[0]
        assert "concisa" in args[0]
