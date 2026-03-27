from typing import Optional

import httpx
from loguru import logger

from app.core.config import settings


class WhatsAppService:
    def __init__(
        self, account_sid: str, auth_token: str, from_number: str, enabled: bool
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.enabled = enabled

    async def send_message(self, to_phone: str, message: str) -> bool:
        if not self.enabled:
            logger.info("[WHATSAPP-DISABLED] to={} (simulated)", to_phone)
            return True

        to_value = (
            to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
        )
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    url,
                    auth=(self.account_sid, self.auth_token),
                    data={
                        "From": self.from_number,
                        "To": to_value,
                        "Body": message,
                    },
                )
            ok = response.status_code == 201
            logger.info(
                "[WHATSAPP] to={} status_code={} ok={}",
                to_phone,
                response.status_code,
                ok,
            )
            return ok
        except Exception as exc:
            logger.error("[WHATSAPP] to={} error={}", to_phone, exc)
            return False

    async def send_policy_confirmation_wa(self, policy, client) -> bool:
        msg = (
            f"Hola {client.first_name}, tu póliza {policy.policy_number} ha sido emitida exitosamente. "
            f"Plan: {policy.plan_version_snapshot.get('name', 'N/A')}. "
            f"Precio: {policy.currency} {float(policy.final_price)}/mes. "
            "¡Gracias por confiar en Yastubo!"
        )
        return await self.send_message(client.phone or "", msg)

    async def send_payment_reminder_wa(self, policy, client) -> bool:
        msg = (
            f"Hola {client.first_name}, tienes un pago pendiente de {policy.currency} {float(policy.final_price)} "
            f"para tu póliza {policy.policy_number}. Por favor actualiza tu forma de pago."
        )
        return await self.send_message(client.phone or "", msg)

    async def send_payment_confirmed_wa(self, policy, client) -> bool:
        msg = (
            f"Hola {client.first_name}, confirmamos el pago de {policy.currency} {float(policy.final_price)} "
            f"para tu póliza {policy.policy_number}. ¡Gracias!"
        )
        return await self.send_message(client.phone or "", msg)


_whatsapp_service_instance: Optional[WhatsAppService] = None


def get_whatsapp_service() -> WhatsAppService:
    global _whatsapp_service_instance
    if _whatsapp_service_instance is None:
        _whatsapp_service_instance = WhatsAppService(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            from_number=settings.TWILIO_WHATSAPP_FROM,
            enabled=settings.WHATSAPP_ENABLED,
        )
    return _whatsapp_service_instance
