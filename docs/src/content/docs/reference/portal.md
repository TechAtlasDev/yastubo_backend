---
title: Portal (Client)
description: Self-service portal for clients — view policies, manage payment methods, and pay pending invoices.
---

Base path: `/api/v1/portal`

All portal endpoints require a valid JWT. The authenticated user's email is automatically matched to a registered client record. A `404` is returned if no client record exists for the user's email.

---

## GET `/portal/me`

Get the client profile linked to the authenticated user.

**Authentication:** Required (any authenticated user)

**Response `200 OK`:** `ClientResponse` object.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "Maria",
  "last_name": "Lopez",
  "email": "maria.lopez@example.com",
  "phone": "+15551234567",
  "birth_date": "1980-06-15",
  "nationality": "MX",
  "country_of_residence": "US",
  "document_type": "PASSPORT",
  "document_number": "A12345678",
  "address": "123 Main St, Los Angeles, CA",
  "created_at": "2024-01-10T08:00:00Z"
}
```

---

## GET `/portal/policies`

List all policies belonging to the authenticated client.

**Authentication:** Required (any authenticated user)

**Response `200 OK`:** Array of `PolicyResponse` objects.

---

## GET `/portal/policies/{policy_id}`

Get details of a specific policy belonging to the authenticated client.

**Authentication:** Required (any authenticated user)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy identifier |

**Response `200 OK`:** `PolicyResponse` object. Returns `404` if the policy does not exist or does not belong to the client.

---

## GET `/portal/policies/{policy_id}/transactions`

List all payment transactions for a specific policy.

**Authentication:** Required (any authenticated user)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy identifier |

**Response `200 OK`:** Array of `TransactionResponse` objects.

---

## POST `/portal/policies/{policy_id}/cancel`

Request cancellation of a policy. The client provides a cancellation reason.

**Authentication:** Required (any authenticated user)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy to cancel |

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | ✅ | Reason for cancellation |

```json
{
  "reason": "I no longer need this coverage"
}
```

**Response `200 OK`:** Updated `PolicyResponse` with `status: "CANCELLED"`.

---

## GET `/portal/payment-methods`

List all saved payment methods for the authenticated user.

**Authentication:** Required (any authenticated user)

**Response `200 OK`:** Array of `PaymentMethod` objects.

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "...",
    "stripe_payment_method_id": "pm_1OxampleXXX",
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2027,
    "is_default": true
  }
]
```

---

## POST `/portal/payment-methods`

Add a new payment method to the user's account.

**Authentication:** Required (any authenticated user)

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stripe_payment_method_id` | string | ✅ | Stripe payment method ID (`pm_...`) obtained from Stripe.js on the frontend |

```json
{
  "stripe_payment_method_id": "pm_1OxampleXXX"
}
```

**Response `200 OK`:** Saved `PaymentMethod` object.

---

## PUT `/portal/payment-methods/{pm_id}/default`

Set a payment method as the default for the user. All other payment methods for the user are unset.

**Authentication:** Required (any authenticated user)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pm_id` | UUID | Payment method identifier |

**Response `200 OK`:** Updated `PaymentMethod` object with `is_default: true`. Returns `404` if not found.

---

## DELETE `/portal/payment-methods/{pm_id}`

Delete a saved payment method.

**Authentication:** Required (any authenticated user)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pm_id` | UUID | Payment method identifier |

**Response `200 OK`:**

```json
{ "status": "deleted" }
```

Returns `404` if the payment method does not exist or belongs to a different user.

---

## POST `/portal/policies/{policy_id}/pay`

Pay a pending policy using the client's default saved payment method.

**Authentication:** Required (any authenticated user)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy to pay |

**Request body:** None — the default payment method on file is used automatically.

**Response `200 OK`:** `TransactionResponse` object.

:::note
The policy must be in `PENDING_PAYMENT` status and the client must have a default payment method saved. Returns `400` otherwise.
:::

---

## Schemas

### PaymentMethod

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Internal identifier |
| `user_id` | UUID | Owning user |
| `stripe_payment_method_id` | string | Stripe `pm_...` identifier |
| `brand` | string | Card brand (e.g. `"visa"`, `"mastercard"`) |
| `last4` | string | Last 4 digits of the card |
| `exp_month` | integer | Expiration month |
| `exp_year` | integer | Expiration year |
| `is_default` | boolean | Whether this is the user's default payment method |

For the `PolicyResponse` and `TransactionResponse` schemas see the [Emission](/reference/emission/) and [Payments](/reference/payments/) reference pages respectively.
