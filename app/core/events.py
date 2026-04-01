import httpx
import asyncio
from typing import Any, Dict, Optional
from loguru import logger
from app.core.config import settings


async def _send_to_n8n(url: str, event: str, data: Dict[str, Any]):
    """Función privada para el envío asíncrono con timeout estricto de 3s."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            payload = {
                "event": event,
                "timestamp": str(asyncio.get_running_loop().time()),
                "data": data,
            }
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"🚀 [n8n] Evento '{event}' enviado con éxito")
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ [n8n] HTTP {e.response.status_code} en '{event}'")
    except Exception as e:
        logger.error(f"❌ [n8n] Fallo al enviar '{event}': {e}")


async def notify_n8n(event_name: str, payload: Dict[str, Any]):
    """
    Dispatcher centralizado con enrutamiento dinámico y fallback.
    Implementa el patrón fire-and-forget mediante create_task.
    """
    # 1. Enrutamiento por tipo de evento
    url = None
    if any(k in event_name for k in ["CLIENT", "LEAD"]):
        url = settings.N8N_WEBHOOK_LEADS
    elif "PAYMENT" in event_name:
        url = settings.N8N_WEBHOOK_PAYMENTS
    elif "POLICY" in event_name:
        url = settings.N8N_WEBHOOK_POLICIES

    # 2. Fallback genérico
    url = url or settings.N8N_WEBHOOK_URL

    if not url:
        return

    # 3. Disparo fire-and-forget validando el event loop
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_send_to_n8n(url, event_name, payload))
    except RuntimeError:
        logger.warning(
            f"⚠️ notify_n8n('{event_name}') llamado fuera de event loop. Ignorando."
        )


# Legacy support (deprecated)
async def dispatch_event(
    event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
) -> bool:
    await notify_n8n(event_type, data)
    return True


def dispatch_event_background(
    event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(notify_n8n(event_type, data))
    except RuntimeError:
        pass
