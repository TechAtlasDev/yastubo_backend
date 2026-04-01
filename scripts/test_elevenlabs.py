from app.core.config import settings
from elevenlabs.client import ElevenLabs
from loguru import logger
import sys


def test_elevenlabs():
    if not settings.ELEVENLABS_API_KEY:
        logger.error("ELEVENLABS_API_KEY is not set in .env")
        sys.exit(1)

    try:
        client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        voices = client.voices.get_all()
        logger.success(f"Successfully connected! Found {len(voices.voices)} voices.")

        for v in voices.voices[:10]:  # Mostrar las primeras 10
            logger.info(f"Voice: {v.name} | ID: {v.voice_id} | Category: {v.category}")
        audio_iter = client.text_to_speech.convert(
            text="Hola, esto es una prueba de conexión con Eleven Labs.",
            voice_id=settings.ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
        )
        audio_content = b"".join(audio_iter)

        if len(audio_content) > 0:
            logger.success(
                f"Generated {len(audio_content)} bytes of audio successfully."
            )
        else:
            logger.warning("Generation succeeded but returned 0 bytes.")

    except Exception as e:
        logger.error(f"Error testing ElevenLabs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_elevenlabs()
