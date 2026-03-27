import httpx
import asyncio
from typing import Any, Dict, Optional
from loguru import logger
from app.core.config import settings


async def dispatch_event(
    event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Sends an event payload to the configured n8n webhook URL.
    This is used to trigger CRM syncs, automated messaging, etc.
    """
    webhook_url = getattr(settings, "N8N_WEBHOOK_URL", None)

    if not webhook_url:
        logger.warning(f"N8N_WEBHOOK_URL not configured. Skipping event: {event_type}")
        return False

    payload = {
        "event_type": event_type,
        "timestamp": str(asyncio.get_event_loop().time()),
        "data": data,
        "metadata": metadata or {},
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Event {event_type} dispatched successfully to n8n.")
            return True
    except Exception as e:
        logger.error(f"Failed to dispatch event {event_type} to n8n: {e}")
        return False


def dispatch_event_background(
    event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
):
    """Fire and forget event dispatch."""
    asyncio.create_task(dispatch_event(event_type, data, metadata))
