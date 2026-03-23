---
title: Emission (Policies)
description: Client registration, policy issuance, status transitions, and PDF download.
---

Base path: `/api/v1/emission`

Endpoints require the `ADMIN` or `VENDEDOR` role unless otherwise noted.

---

## POST `/emission/clients`

Register a new client in the system.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | ✅ | Client's first name |
| `last_name` | string | ✅ | Client's last name |
| `email` | string (email) | ✅ | Client email address |
| `phone` | string | ❌ | Phone number |
| `birth_date` | date (`YYYY-MM-DD`) | ✅ | Date of birth |
| `nationality` | string (2 chars) | ✅ | ISO-3166-1 alpha-2 nationality code (auto-uppercased) |
| `country_of_residence` | string (2 chars) | ✅ | ISO-3166-1 alpha-2 country of residence (auto-uppercased) |
| `document_type` | string | ✅ | Document type (e.g. `"PASSPORT"`, `"ID_CARD"`) |
| `document_number` | string | ✅ | Document identification number |
| `address` | string | ❌ | Physical address |

```json
{
  "first_name": "Maria",
  "last_name": "Lopez",
  "email": "maria.lopez@example.com",
  "phone": "+15551234567",
  "birth_date": "1980-06-15",
  "nationality": "MX",
  "country_of_residence": "US",
  "document_type": "PASSPORT",
  "document_number": "A12345678",
  "address": "123 Main St, Los Angeles, CA"
}
```

**Response `201 Created`:**

```json
{
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
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## GET `/emission/clients/{client_id}`

Retrieve a client's details.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `client_id` | UUID | Client identifier |

**Response `200 OK`:** `ClientResponse` object. Returns `404` if not found.

---

## POST `/emission/issue`

Issue (create) a new insurance policy for a registered client.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | UUID | ✅ | ID of the registered client |
| `plan_id` | UUID | ✅ | ID of the plan to issue |
| `country_code` | string (2 chars) | ✅ | Client's country code for pricing (auto-uppercased) |
| `start_date` | date (`YYYY-MM-DD`) | ✅ | Policy start date — must be today or in the future |
| `notes` | string | ❌ | Internal notes |

```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id":   "661f9511-f3ac-52e5-b827-557766551111",
  "country_code": "US",
  "start_date": "2024-02-01",
  "notes": "Referred by agent #42"
}
```

**Response `201 Created`:** `PolicyResponse` object. The policy is created with status `DRAFT`.

---

## GET `/emission/policies`

List policies, optionally filtered.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by policy status (see [Policy Statuses](#policy-statuses)) |
| `client_id` | UUID | Filter by client |

**Response `200 OK`:** Array of `PolicyResponse` objects.

---

## GET `/emission/policies/{policy_id}`

Get details of a specific policy.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy identifier |

**Response `200 OK`:** `PolicyResponse` object. Returns `404` if not found.

---

## POST `/emission/policies/{policy_id}/transition`

Manually change the status of a policy.

**Authentication:** Required — `ADMIN` role only

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy identifier |

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_status` | PolicyStatus | ✅ | Desired new status (see [Policy Statuses](#policy-statuses)) |
| `reason` | string | ❌ | Reason for the transition (stored in history) |

```json
{
  "target_status": "ACTIVE",
  "reason": "Payment confirmed manually"
}
```

**Response `200 OK`:** Updated `PolicyResponse` object.

:::caution
Only valid transitions are allowed. Attempting an invalid transition returns `400 Bad Request`.
:::

---

## GET `/emission/policies/{policy_id}/pdf`

Download the generated PDF for a policy.

**Authentication:** Required — `ADMIN` or `VENDEDOR`

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy_id` | UUID | Policy identifier |

**Response `200 OK`:** Binary `application/pdf` file with filename `{policy_number}.pdf`.

Returns `404` if no PDF has been generated for the policy yet.

---

## Policy Statuses

Policies follow a strict state machine. The table below shows all statuses and valid transitions:

| Status | Description | Valid next statuses |
|--------|-------------|---------------------|
| `DRAFT` | Newly created, no payment yet | `PENDING_PAYMENT`, `CANCELLED` |
| `PENDING_PAYMENT` | Awaiting first payment | `ACTIVE`, `CANCELLED`, `IN_ARREARS` |
| `ACTIVE` | Fully active coverage | `IN_ARREARS`, `CANCELLED`, `CASE_REPORTED` |
| `IN_ARREARS` | Payment overdue | `ACTIVE`, `CANCELLED` |
| `CANCELLED` | Permanently cancelled | *(terminal)* |
| `CASE_REPORTED` | A claim has been reported | `CASE_IN_PROGRESS`, `CANCELLED` |
| `CASE_IN_PROGRESS` | Claim being processed | `CASE_CLOSED` |
| `CASE_CLOSED` | Claim resolved | *(terminal)* |

---

## Schemas

### ClientResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Client identifier |
| `first_name` | string | First name |
| `last_name` | string | Last name |
| `email` | string | Email address |
| `phone` | string \| null | Phone number |
| `birth_date` | date | Date of birth |
| `nationality` | string | Nationality country code |
| `country_of_residence` | string | Country of residence code |
| `document_type` | string | Document type |
| `document_number` | string | Document number |
| `address` | string \| null | Physical address |
| `created_at` | datetime | Registration timestamp |

### PolicyResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Policy identifier |
| `policy_number` | string | Human-readable policy number |
| `client_id` | UUID | Linked client |
| `plan_id` | UUID | Linked plan |
| `status` | string | Current policy status |
| `base_price` | decimal | Plan base price at issuance |
| `surcharge_amount` | decimal | Age/country surcharge |
| `final_price` | decimal | Total monthly price |
| `currency` | string | Currency code |
| `country_code` | string | Country used for pricing |
| `insured_age` | integer | Age of insured at issuance |
| `start_date` | date \| null | Coverage start date |
| `end_date` | date \| null | Coverage end date |
| `pdf_path` | string \| null | Server path to the generated PDF |
| `notes` | string \| null | Internal notes |
| `issued_by` | UUID | User who issued the policy |
| `issued_at` | datetime \| null | Issuance timestamp |
| `client` | ClientResponse | Nested client details |
| `status_history` | StatusHistoryResponse[] | Status change log |

### StatusHistoryResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | History entry identifier |
| `from_status` | string \| null | Previous status |
| `to_status` | string | New status |
| `changed_by` | UUID | User who made the change |
| `reason` | string \| null | Reason for the change |
| `changed_at` | datetime | Timestamp of the change |
