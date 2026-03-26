import json
import base64
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from app.core.config import settings
from app.modules.ai.service import get_ai_service
from elevenlabs.client import ElevenLabs
import uuid

router = APIRouter(prefix="/voice", tags=["Voice AI"])

# Initialize ElevenLabs
el_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

@router.websocket("/stream")
async def voice_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Twilio Voice Stream WebSocket connected")
    
    stream_sid = None
    ai_service = get_ai_service()
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data['event'] == 'start':
                stream_sid = data['start']['streamSid']
                logger.info(f"Stream started: {stream_sid}")
                
            elif data['event'] == 'media':
                # Twilio sends media as base64 encoded mulaw 8000Hz
                payload = data['media']['payload']
                # In a real RAG-Voice scenario, we would:
                # 1. Accumulate audio chunks
                # 2. Use VAD (Voice Activity Detection)
                # 3. Use Whisper/Gemini for STT
                # 4. Use AI Service for response
                # 5. Use ElevenLabs for TTS
                # 6. Send back to Twilio
                
                # MOCK RESPONSE (For MVP Phase 4 structure)
                # We'll implement the actual bridge logic here
                pass
                
            elif data['event'] == 'stop':
                logger.info(f"Stream stopped: {stream_sid}")
                break
                
    except WebSocketDisconnect:
        logger.info("Twilio Voice Stream WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in Voice Stream: {e}")

@router.post("/incoming-call")
async def incoming_call():
    """ TwiML for Twilio to connect the call to our WebSocket """
    from fastapi.responses import Response
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say language="es-ES">Hola, bienvenido a Yastubo. Un momento mientras te conectamos con nuestro asistente de IA.</Say>
        <Connect>
            <Stream url="wss://{settings.APP_NAME.lower().replace(' ', '-')}.loca.lt/api/v1/voice/stream" />
        </Connect>
    </Response>
    """
    return Response(content=twiml, media_type="application/xml")
