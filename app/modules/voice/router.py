import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from app.core.config import settings
from app.modules.ai.service import get_ai_service
from elevenlabs.client import ElevenLabs

router = APIRouter(prefix="/voice", tags=["Voice AI"])

# Initialize ElevenLabs
el_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)


@router.websocket("/stream")
async def voice_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Twilio Voice Stream WebSocket connected")

    stream_sid = None
    get_ai_service()

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data["event"] == "start":
                stream_sid = data["start"]["streamSid"]
                logger.info(f"Stream started: {stream_sid}")

            elif data["event"] == "media":
                # Twilio sends media as base64 encoded mulaw 8000Hz

                # BRIDGE LOGIC (Phase 4):

                # 1. We mock STT for now as we don't have a 8000Hz mulaw parser here
                # but we'll simulate the AI processing and ElevenLabs TTS

                # AI RESPONSE
                ai_service = get_ai_service()
                # For demo purposes, we'll respond to "hola" if we detected sound (mocked)
                response_text = await ai_service.voice_chat(
                    "Hola, necesito ayuda con mi póliza."
                )

                # ELEVENLABS TTS
                # ElevenLabs returns binary audio. We convert to base64 and send to Twilio.
                # In a real scenario, this would be streamed.
                audio_iter = el_client.generate(
                    text=response_text,
                    voice="Rachel",  # Empathetic Spanish voice
                    model="eleven_multilingual_v2",
                )

                import base64

                audio_bytes = b"".join(audio_iter)
                encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

                # Send back to Twilio
                await websocket.send_json(
                    {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": encoded_audio},
                    }
                )

                logger.info(f"Sent AI voice response: {response_text}")

            elif data["event"] == "stop":
                logger.info(f"Stream stopped: {stream_sid}")
                break

    except WebSocketDisconnect:
        logger.info("Twilio Voice Stream WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in Voice Stream: {e}")


@router.post("/incoming-call")
async def incoming_call():
    """TwiML for Twilio to connect the call to our WebSocket"""
    from fastapi.responses import Response

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say language="es-ES">Hola, bienvenido a Yastubo. Un momento mientras te conectamos con nuestro asistente de IA.</Say>
        <Connect>
            <Stream url="wss://{settings.APP_NAME.lower().replace(" ", "-")}.loca.lt/api/v1/voice/stream" />
        </Connect>
    </Response>
    """
    return Response(content=twiml, media_type="application/xml")
