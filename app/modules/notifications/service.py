from typing import Optional

from app.modules.notifications.email_service import EmailService, get_email_service
from app.modules.notifications.whatsapp_service import WhatsAppService, get_whatsapp_service


class NotificationsService:
    def __init__(self, email: EmailService, whatsapp: WhatsAppService):
        self.email = email
        self.whatsapp = whatsapp

    async def on_policy_issued(self, policy, client, pdf_bytes: bytes) -> None:
        await self.email.send_policy_confirmation(policy, client, pdf_bytes)
        await self.whatsapp.send_policy_confirmation_wa(policy, client)

    async def on_payment_confirmed(self, policy, client, transaction) -> None:
        await self.email.send_payment_confirmed(policy, client, transaction)
        await self.whatsapp.send_payment_confirmed_wa(policy, client)

    async def on_payment_failed(self, policy, client, attempt: int) -> None:
        await self.email.send_payment_failed(policy, client, attempt)
        if attempt >= 2:
            await self.whatsapp.send_payment_reminder_wa(policy, client)

    async def on_payment_reminder(self, policy, client) -> None:
        await self.email.send_payment_reminder(policy, client)
        await self.whatsapp.send_payment_reminder_wa(policy, client)

    async def on_policy_cancelled(self, policy, client) -> None:
        await self.email.send_cancellation(policy, client)


_notifications_service_instance: Optional[NotificationsService] = None


def get_notifications_service() -> NotificationsService:
    global _notifications_service_instance
    if _notifications_service_instance is None:
        _notifications_service_instance = NotificationsService(
            email=get_email_service(),
            whatsapp=get_whatsapp_service(),
        )
    return _notifications_service_instance
