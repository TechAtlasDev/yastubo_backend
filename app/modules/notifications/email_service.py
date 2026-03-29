import base64
from pathlib import Path
from typing import Any, Optional

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger

from app.core.config import settings


class EmailService:
    def __init__(
        self,
        api_key: str,
        from_email: str,
        from_name: str,
        enabled: bool,
    ):
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
        self.enabled = enabled

        templates_dir = (Path(__file__).parent / "templates").resolve()
        if not templates_dir.exists():
            logger.error(f"Email templates directory not found at: {templates_dir}")

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> bool:
        if not self.enabled:
            logger.info(
                "[EMAIL-DISABLED] to={} subject={} (simulated)",
                to_email,
                subject,
            )
            return True

        payload: dict[str, Any] = {
            "personalizations": [
                {
                    "to": [{"email": to_email, "name": to_name}],
                    "subject": subject,
                }
            ],
            "from": {"email": self.from_email, "name": self.from_name},
            "content": [{"type": "text/html", "value": html_content}],
        }

        if attachments:
            payload["attachments"] = attachments

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

            ok = response.status_code == 202
            logger.info(
                "[EMAIL] to={} subject={} status_code={} ok={}",
                to_email,
                subject,
                response.status_code,
                ok,
            )
            return ok
        except Exception as exc:
            logger.error("[EMAIL] to={} subject={} error={}", to_email, subject, exc)
            return False

    async def send_policy_confirmation(self, policy, client, pdf_bytes: bytes) -> bool:
        html = self.jinja_env.get_template("email_policy_confirmation.html").render(
            client_name=f"{client.first_name} {client.last_name}",
            policy_number=policy.policy_number,
            plan_name=policy.plan_version_snapshot.get("name", "N/A"),
            currency=policy.currency,
            final_price=float(policy.final_price),
        )

        attachment = {
            "filename": f"{policy.policy_number}.pdf",
            "content": base64.b64encode(pdf_bytes).decode("utf-8"),
            "type": "application/pdf",
            "disposition": "attachment",
        }

        return await self.send(
            to_email=client.email,
            to_name=f"{client.first_name} {client.last_name}",
            subject=f"Confirmación de póliza {policy.policy_number}",
            html_content=html,
            attachments=[attachment],
        )

    async def send_payment_reminder(self, policy, client) -> bool:
        html = self.jinja_env.get_template("email_payment_reminder.html").render(
            client_name=f"{client.first_name} {client.last_name}",
            policy_number=policy.policy_number,
            amount=float(policy.final_price),
            currency=policy.currency,
            payment_link=f"{settings.FRONTEND_URL}/portal/policies/{policy.id}",
        )
        return await self.send(
            to_email=client.email,
            to_name=f"{client.first_name} {client.last_name}",
            subject=f"Recordatorio de pago - Póliza {policy.policy_number}",
            html_content=html,
        )

    async def send_payment_failed(self, policy, client, attempt: int) -> bool:
        html = self.jinja_env.get_template("email_payment_failed.html").render(
            client_name=f"{client.first_name} {client.last_name}",
            policy_number=policy.policy_number,
            amount=float(policy.final_price),
            currency=policy.currency,
            attempt=attempt,
            urgent_message=(
                "Actualiza tu tarjeta cuanto antes para evitar la suspensión del servicio."
                if attempt >= 2
                else ""
            ),
        )
        return await self.send(
            to_email=client.email,
            to_name=f"{client.first_name} {client.last_name}",
            subject=f"Pago fallido - Póliza {policy.policy_number}",
            html_content=html,
        )

    async def send_payment_confirmed(self, policy, client, transaction) -> bool:
        html = self.jinja_env.get_template("email_payment_confirmed.html").render(
            client_name=f"{client.first_name} {client.last_name}",
            policy_number=policy.policy_number,
            amount=float(transaction.amount),
            currency=transaction.currency,
            transaction_id=transaction.id,
        )
        return await self.send(
            to_email=client.email,
            to_name=f"{client.first_name} {client.last_name}",
            subject=f"Pago confirmado - Póliza {policy.policy_number}",
            html_content=html,
        )

    async def send_cancellation(self, policy, client) -> bool:
        html = self.jinja_env.get_template("email_cancellation.html").render(
            client_name=f"{client.first_name} {client.last_name}",
            policy_number=policy.policy_number,
        )
        return await self.send(
            to_email=client.email,
            to_name=f"{client.first_name} {client.last_name}",
            subject=f"Anulación de póliza {policy.policy_number}",
            html_content=html,
        )


_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService(
            api_key=settings.SENDGRID_API_KEY,
            from_email=settings.EMAIL_FROM,
            from_name=settings.EMAIL_FROM_NAME,
            enabled=settings.NOTIFICATIONS_ENABLED,
        )
    return _email_service_instance
