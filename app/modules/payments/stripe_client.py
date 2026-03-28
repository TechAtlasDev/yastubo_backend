import asyncio
import stripe
from typing import Optional
from app.core.config import settings


class StripeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        stripe.api_key = api_key

    async def create_customer(self, email: str, name: str, metadata: dict) -> dict:
        return await asyncio.to_thread(
            stripe.Customer.create, email=email, name=name, metadata=metadata
        )

    async def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        customer_id: str,
        payment_method_id: Optional[str],
        metadata: dict,
    ) -> dict:
        params = {
            "amount": amount_cents,
            "currency": currency,
            "customer": customer_id,
            "metadata": metadata,
            "automatic_payment_methods": {"enabled": True, "allow_redirects": "always"},
        }
        if payment_method_id:
            params["payment_method"] = payment_method_id

        return await asyncio.to_thread(stripe.PaymentIntent.create, **params)

    async def confirm_payment_intent(
        self, pi_id: str, payment_method_id: Optional[str] = None
    ) -> dict:
        params = {}
        if payment_method_id:
            params["payment_method"] = payment_method_id
        return await asyncio.to_thread(
            stripe.PaymentIntent.confirm,
            pi_id,
            **params,
        )

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: str,
        metadata: dict,
        connect_account_id: Optional[str] = None,
        application_fee_percent: Optional[float] = None,
    ) -> dict:
        # First attach PM to customer
        await asyncio.to_thread(
            stripe.PaymentMethod.attach, payment_method_id, customer=customer_id
        )
        # Set as default
        await asyncio.to_thread(
            stripe.Customer.modify,
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )

        params = {
            "customer": customer_id,
            "items": [{"price": price_id}],
            "metadata": metadata,
            "expand": ["latest_invoice.payment_intent"],
        }

        if connect_account_id:
            params["application_fee_percent"] = application_fee_percent
            params["transfer_data"] = {"destination": connect_account_id}

        return await asyncio.to_thread(stripe.Subscription.create, **params)

    async def cancel_subscription(
        self, subscription_id: str, at_period_end: bool
    ) -> dict:
        if at_period_end:
            return await asyncio.to_thread(
                stripe.Subscription.modify, subscription_id, cancel_at_period_end=True
            )
        else:
            return await asyncio.to_thread(stripe.Subscription.delete, subscription_id)

    async def create_connect_account(self, email: str, metadata: dict) -> dict:
        return await asyncio.to_thread(
            stripe.Account.create,
            type="express",
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            metadata=metadata,
        )

    async def create_account_link(
        self, account_id: str, refresh_url: str, return_url: str
    ) -> dict:
        return await asyncio.to_thread(
            stripe.AccountLink.create,
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

    async def get_payment_method(self, pm_id: str) -> dict:
        try:
            return await asyncio.to_thread(stripe.PaymentMethod.retrieve, pm_id)
        except stripe.error.InvalidRequestError as e:
            raise ValueError(f"Stripe PaymentMethod not found: {e}") from e
        except stripe.error.StripeError as e:
            raise RuntimeError(f"Stripe error retrieving payment method: {e}") from e

    async def get_customer_id_by_email(self, email: str) -> Optional[str]:
        try:
            customers = await asyncio.to_thread(
                stripe.Customer.list, email=email, limit=1
            )
            if customers and customers.get("data"):
                return customers["data"][0]["id"]
            return None
        except stripe.error.StripeError as e:
            raise RuntimeError(f"Stripe error looking up customer by email: {e}") from e

    async def construct_webhook_event(
        self, payload: bytes, sig_header: str, secret: str
    ) -> dict:
        return stripe.Webhook.construct_event(payload, sig_header, secret)


_stripe_instance: Optional[StripeClient] = None


def get_stripe_client() -> StripeClient:
    global _stripe_instance
    if _stripe_instance is None:
        _stripe_instance = StripeClient(settings.STRIPE_SECRET_KEY)
    return _stripe_instance
