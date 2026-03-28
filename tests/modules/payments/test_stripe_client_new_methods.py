"""Unit tests for DT-03 and DT-04: StripeClient.get_payment_method and
get_customer_id_by_email."""

import pytest
from unittest.mock import patch
import stripe

from app.modules.payments.stripe_client import StripeClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_client() -> StripeClient:
    return StripeClient(api_key="sk_test_fake")


# ---------------------------------------------------------------------------
# DT-03: get_payment_method
# ---------------------------------------------------------------------------

class TestGetPaymentMethod:
    @pytest.mark.asyncio
    async def test_returns_payment_method_dict(self):
        pm_data = {
            "id": "pm_123",
            "object": "payment_method",
            "type": "card",
            "card": {"brand": "visa", "last4": "4242", "exp_month": 12, "exp_year": 2030},
        }
        client = _make_client()
        with patch("stripe.PaymentMethod.retrieve", return_value=pm_data) as mock_retrieve:
            result = await client.get_payment_method("pm_123")

        mock_retrieve.assert_called_once_with("pm_123")
        assert result == pm_data
        assert result["card"]["last4"] == "4242"

    @pytest.mark.asyncio
    async def test_raises_value_error_on_invalid_request(self):
        client = _make_client()
        err = stripe.error.InvalidRequestError("No such payment_method", param="id")
        with patch("stripe.PaymentMethod.retrieve", side_effect=err):
            with pytest.raises(ValueError, match="Stripe PaymentMethod not found"):
                await client.get_payment_method("pm_invalid")

    @pytest.mark.asyncio
    async def test_raises_runtime_error_on_stripe_error(self):
        client = _make_client()
        err = stripe.error.AuthenticationError("Invalid API key")
        with patch("stripe.PaymentMethod.retrieve", side_effect=err):
            with pytest.raises(RuntimeError, match="Stripe error retrieving payment method"):
                await client.get_payment_method("pm_123")


# ---------------------------------------------------------------------------
# DT-04: get_customer_id_by_email
# ---------------------------------------------------------------------------

class TestGetCustomerIdByEmail:
    @pytest.mark.asyncio
    async def test_returns_customer_id_when_found(self):
        customers_response = {
            "object": "list",
            "data": [{"id": "cus_abc123", "email": "user@example.com"}],
            "has_more": False,
        }
        client = _make_client()
        with patch("stripe.Customer.list", return_value=customers_response) as mock_list:
            result = await client.get_customer_id_by_email("user@example.com")

        mock_list.assert_called_once_with(email="user@example.com", limit=1)
        assert result == "cus_abc123"

    @pytest.mark.asyncio
    async def test_returns_none_when_no_customer_found(self):
        customers_response = {"object": "list", "data": [], "has_more": False}
        client = _make_client()
        with patch("stripe.Customer.list", return_value=customers_response):
            result = await client.get_customer_id_by_email("unknown@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_raises_runtime_error_on_stripe_error(self):
        client = _make_client()
        err = stripe.error.APIConnectionError("Network error")
        with patch("stripe.Customer.list", side_effect=err):
            with pytest.raises(RuntimeError, match="Stripe error looking up customer by email"):
                await client.get_customer_id_by_email("user@example.com")

    @pytest.mark.asyncio
    async def test_returns_none_when_data_key_missing(self):
        # Defensive: if Stripe returns unexpected shape
        customers_response = {"object": "list"}
        client = _make_client()
        with patch("stripe.Customer.list", return_value=customers_response):
            result = await client.get_customer_id_by_email("user@example.com")

        assert result is None
