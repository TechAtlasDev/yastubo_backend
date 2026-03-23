---
title: Plans
description: Funeral insurance plan management — create, update, price calculation, and versioning.
---

Base path: `/api/v1/plans`

All endpoints require a valid JWT. Write operations (create/update/toggle) require the `ADMIN` role.

---

## GET `/plans`

List all funeral insurance plans.

**Authentication:** Required (any role)

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active_only` | boolean | `true` | When `true`, only returns plans where `is_active = true` |

**Response `200 OK`:** Array of `PlanResponse` objects.

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Plan Básico",
    "description": "Basic funeral coverage for migrants",
    "base_price": "150.00",
    "currency": "USD",
    "is_active": true,
    "max_entry_age": 65,
    "max_renewal_age": 75,
    "repatriation_countries": ["MX", "GT", "SV"],
    "terms_es": "...",
    "terms_en": "...",
    "coverages": [...],
    "age_ranges": [...],
    "country_configs": [...],
    "current_version": 3,
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

---

## POST `/plans`

Create a new funeral insurance plan.

**Authentication:** Required — `ADMIN` role

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Plan name |
| `description` | string | ❌ | Plan description |
| `base_price` | decimal | ✅ | Base monthly price |
| `currency` | string | ❌ | Currency code (default: `"USD"`) |
| `max_entry_age` | integer | ✅ | Maximum age to enroll |
| `max_renewal_age` | integer | ✅ | Maximum age to renew coverage |
| `repatriation_countries` | string[] | ✅ | ISO-3166-1 alpha-2 country codes covered for repatriation |
| `terms_es` | string | ❌ | Terms and conditions in Spanish |
| `terms_en` | string | ❌ | Terms and conditions in English |
| `age_ranges` | AgeRangeCreate[] | ✅ | Age bracket surcharge rules |
| `country_configs` | CountryConfigCreate[] | ✅ | Per-country pricing overrides |
| `coverage_ids` | UUID[] | ✅ | IDs of coverage items to include in the plan |

**AgeRangeCreate:**

| Field | Type | Description |
|-------|------|-------------|
| `min_age` | integer | Minimum age (inclusive) |
| `max_age` | integer | Maximum age (inclusive) |
| `surcharge_percentage` | decimal | Percentage surcharge applied to the base price |

**CountryConfigCreate:**

| Field | Type | Description |
|-------|------|-------------|
| `country_code` | string (2 chars) | ISO-3166-1 alpha-2 country code (auto-uppercased) |
| `country_name` | string | Human-readable country name |
| `base_price_override` | decimal \| null | Override base price for this country |
| `is_available` | boolean | Whether the plan is available in this country (default: `true`) |

```json
{
  "name": "Plan Familiar",
  "description": "Family funeral coverage",
  "base_price": "200.00",
  "currency": "USD",
  "max_entry_age": 70,
  "max_renewal_age": 80,
  "repatriation_countries": ["MX", "GT"],
  "age_ranges": [
    { "min_age": 0,  "max_age": 45, "surcharge_percentage": "0.00" },
    { "min_age": 46, "max_age": 60, "surcharge_percentage": "15.00" },
    { "min_age": 61, "max_age": 70, "surcharge_percentage": "30.00" }
  ],
  "country_configs": [
    { "country_code": "MX", "country_name": "Mexico", "is_available": true },
    { "country_code": "GT", "country_name": "Guatemala", "base_price_override": "180.00", "is_available": true }
  ],
  "coverage_ids": ["<uuid>", "<uuid>"]
}
```

**Response `201 Created`:** `PlanResponse` object.

---

## GET `/plans/{plan_id}`

Get details of a specific plan.

**Authentication:** Required (any role)

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan_id` | UUID | Plan identifier |

**Response `200 OK`:** `PlanResponse` object. Returns `404` if not found.

---

## PUT `/plans/{plan_id}`

Update an existing plan. Every successful update creates a new version snapshot.

**Authentication:** Required — `ADMIN` role

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan_id` | UUID | Plan identifier |

**Request body:** Same fields as `PlanCreate`, all optional (`PlanUpdate`).

**Response `200 OK`:** Updated `PlanResponse` object.

---

## PATCH `/plans/{plan_id}/toggle`

Toggle the `is_active` status of a plan (activate ↔ deactivate).

**Authentication:** Required — `ADMIN` role

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan_id` | UUID | Plan identifier |

**Request body:** None

**Response `200 OK`:** Updated `PlanResponse` object with the new `is_active` value.

---

## POST `/plans/calculate-price`

Calculate the final price for a plan given a client's age and country.

**Authentication:** Required (any role)

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_id` | UUID | ✅ | Plan to price |
| `age` | integer (0–120) | ✅ | Client's age |
| `country_code` | string (2 chars) | ✅ | Client's country of residence (auto-uppercased) |
| `quantity` | integer (≥1) | ❌ | Number of insured (default: `1`) |

```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "age": 52,
  "country_code": "MX",
  "quantity": 1
}
```

**Response `200 OK`:**

```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_name": "Plan Familiar",
  "base_price": "200.00",
  "country_override": null,
  "age_surcharge_percentage": "15.00",
  "age_surcharge_amount": "30.00",
  "final_price": "230.00",
  "currency": "USD",
  "breakdown": {
    "base": "200.00",
    "age_surcharge": "30.00",
    "country_override": null,
    "total": "230.00"
  }
}
```

---

## GET `/plans/{plan_id}/versions`

List all historical versions of a plan (newest first).

**Authentication:** Required — `ADMIN` role

**Path parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan_id` | UUID | Plan identifier |

**Response `200 OK`:** Array of `PlanVersion` objects ordered by `version_number` descending.

---

## Schemas

### PlanResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Plan identifier |
| `name` | string | Plan name |
| `description` | string \| null | Plan description |
| `base_price` | decimal | Monthly base price |
| `currency` | string | Currency code |
| `is_active` | boolean | Whether the plan is currently active |
| `max_entry_age` | integer | Maximum enrollment age |
| `max_renewal_age` | integer | Maximum renewal age |
| `repatriation_countries` | string[] | Country codes covered |
| `terms_es` | string \| null | Terms in Spanish |
| `terms_en` | string \| null | Terms in English |
| `coverages` | CoverageResponse[] | Included coverage items |
| `age_ranges` | AgeRangeCreate[] | Age bracket surcharge rules |
| `country_configs` | CountryConfigCreate[] | Per-country configuration |
| `current_version` | integer | Current version number |
| `created_at` | datetime | Creation timestamp |

### CoverageResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Coverage item identifier |
| `name` | string | Coverage name |
| `description` | string \| null | Coverage description |
| `limit_amount` | decimal \| null | Maximum benefit amount |
| `limit_unit` | string \| null | Unit for the limit (e.g. `"USD"`) |
| `notes_es` | string \| null | Notes in Spanish |
| `notes_en` | string \| null | Notes in English |
