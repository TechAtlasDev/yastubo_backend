---
title: Payments
description: Stripe payment intents, subscriptions, manual payments, transactions, and Connect onboarding.
---

Base path: `/api/v1/payments`

---

## POST `/payments/intent`

Create a Stripe **one-time payment intent** for a policy.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | UUID | ✅ | Policy to pay |
| `payment_method_id` | string | ❌ | Stripe payment method ID (e.g. `pm_...`). If omitted, the client must confirm the payment on the frontend. |
| `save_payment_method` | boolean | ❌ | Save the payment method for future use (default: `false`) |

```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_method_id": "pm_1Oxample...",
  "save_payment_method": true
}
```

**Response `200 OK`:** `TransactionResponse` (includes `client_secret` for frontend confirmation).

```json
{
  "id": "...",
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "stripe_payment_intent_id": "pi_1OxampleXXX",
  "stripe_invoice_id": null,
  "amount": "230.00",
  "currency": "USD",
  "status": "requires_confirmation",
  "payment_type": "one_time",
  "processed_at": null,
  "client_secret": "pi_1OxampleXXX_secret_YYY"
}
```

:::tip
Use the `client_secret` with Stripe.js on the frontend to complete the payment confirmation.
:::

---

## POST `/payments/subscription`

Create a recurring Stripe **subscription** for a policy.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | UUID | ✅ | Policy to subscribe |
| `stripe_payment_method_id` | string | ✅ | Stripe payment method ID (`pm_...`) |
| `billing_anchor_day` | integer (1–28) | ❌ | Day of month for billing. Defaults to start date day. |

```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "stripe_payment_method_id": "pm_1OxampleXXX",
  "billing_anchor_day": 15
}
```

**Response `200 OK`:** `SubscriptionResponse` object.

```json
{
  "id": "...",
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "stripe_subscription_id": "sub_1OxampleXXX",
  "status": "active",
  "current_period_start": "2024-02-15T00:00:00Z",
  "current_period_end": "2024-03-15T00:00:00Z",
  "cancel_at_period_end": false
}
```

---

## POST `/payments/subscription/cancel`

Cancel an active subscription.

**Authentication:** Required — `ADMIN` role only

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | UUID | ✅ | Policy whose subscription to cancel |
| `cancel_immediately` | boolean | ❌ | If `true`, cancels immediately; if `false` (default), cancels at the end of the current billing period |

```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "cancel_immediately": false
}
```

**Response `200 OK`:** Updated `SubscriptionResponse` with `cancel_at_period_end: true` (or `status: "cancelled"` if cancelled immediately).

---

## POST `/payments/manual`

Register a manual payment (cash, bank transfer, etc.) for a policy.

**Authentication:** Required — `ADMIN` role only

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | UUID | ✅ | Policy receiving the payment |
| `amount` | decimal | ✅ | Amount paid |
| `notes` | string | ❌ | Notes about the manual payment |

```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": "230.00",
  "notes": "Cash payment received at office"
}
```

**Response `200 OK`:** `TransactionResponse` object with `payment_type: "manual"`.

---

## GET `/payments/transactions`

List payment transactions, optionally filtered.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Filter by policy |
| `status` | string | Filter by transaction status (e.g. `"succeeded"`, `"pending"`, `"failed"`) |

**Response `200 OK`:** Array of `TransactionResponse` objects.

---

## POST `/payments/connect/onboarding`

Generate a Stripe Connect onboarding link for the current user (to become a connected account).

**Authentication:** Required (any authenticated user)

**Request body:** None

**Response `200 OK`:**

```json
{
  "url": "https://connect.stripe.com/setup/s/xxxx",
  "account_id": "acct_1OxampleXXX"
}
```

Redirect the user to `url` to complete the Stripe Connect onboarding.

---

## POST `/payments/webhook`

Receive and process Stripe webhook events. This endpoint should be registered in your Stripe dashboard.

**Authentication:** Stripe signature verification via `stripe-signature` header (no JWT required)

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `stripe-signature` | ✅ | Stripe webhook signature for payload verification |

**Request body:** Raw Stripe event payload (JSON)

**Response `200 OK`:**

```json
{ "status": "success" }
```

Events are processed asynchronously in a background task.

:::caution
Never expose this endpoint without verifying the `stripe-signature` header. The endpoint returns `400` if the signature is missing or invalid.
:::

---

## Schemas

### TransactionResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Transaction identifier |
| `policy_id` | UUID | Associated policy |
| `stripe_payment_intent_id` | string \| null | Stripe Payment Intent ID |
| `stripe_invoice_id` | string \| null | Stripe Invoice ID (for subscriptions) |
| `amount` | decimal | Payment amount |
| `currency` | string | Currency code |
| `status` | string | Transaction status (`pending`, `succeeded`, `failed`, etc.) |
| `payment_type` | string | `"one_time"`, `"subscription"`, or `"manual"` |
| `processed_at` | datetime \| null | When the payment was confirmed |
| `client_secret` | string \| null | Stripe client secret — only present on payment intent creation |

### SubscriptionResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Internal subscription identifier |
| `policy_id` | UUID | Associated policy |
| `stripe_subscription_id` | string | Stripe subscription ID (`sub_...`) |
| `status` | string | Stripe subscription status (`active`, `past_due`, `cancelled`, etc.) |
| `current_period_start` | datetime | Start of the current billing period |
| `current_period_end` | datetime | End of the current billing period |
| `cancel_at_period_end` | boolean | Whether the subscription is set to cancel at period end |

### ConnectOnboardingResponse

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Stripe Connect onboarding URL |
| `account_id` | string | Stripe connected account ID |
