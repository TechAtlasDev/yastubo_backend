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

    async def retrieve_subscription(self, subscription_id: str) -> dict:
        return await asyncio.to_thread(stripe.Subscription.retrieve, subscription_id)

    async def update_subscription_item_price(
        self,
        subscription_id: str,
        new_amount_cents: int,
        currency: str,
    ) -> dict:
        """Update the first subscription item to a new unit amount using price_data."""
        sub = await asyncio.to_thread(stripe.Subscription.retrieve, subscription_id)
        item = sub["items"]["data"][0]
        item_id = item["id"]
        product_id = item["price"]["product"]
        billing_interval = item["price"]["recurring"]["interval"]
        return await asyncio.to_thread(
            stripe.SubscriptionItem.modify,
            item_id,
            price_data={
                "currency": currency,
                "product": product_id,
                "unit_amount": new_amount_cents,
                "recurring": {"interval": billing_interval},
            },
            proration_behavior="none",
        )

    async def get_payment_method(self, pm_id: str) -> dict:
        return await asyncio.to_thread(stripe.PaymentMethod.retrieve, pm_id)

    async def get_customer_id_by_email(self, email: str) -> Optional[str]:
        customers = await asyncio.to_thread(stripe.Customer.list, email=email, limit=1)
        if customers and customers.data:
            return customers.data[0].id
        return None

    async def construct_webhook_event(
        self, payload: bytes, sig_header: str, secret: str
    ) -> dict:
        return stripe.Webhook.construct_event(payload, sig_header, secret)

    async def retrieve_payment_intent(self, pi_id: str) -> dict:
        return await asyncio.to_thread(stripe.PaymentIntent.retrieve, pi_id)


_stripe_instance: Optional[StripeClient] = None


def get_stripe_client() -> StripeClient:
    global _stripe_instance
    if _stripe_instance is None:
        _stripe_instance = StripeClient(settings.STRIPE_SECRET_KEY)
    return _stripe_instance
