---
title: API Overview
description: Base URL, authentication, versioning, and error codes for the Yastubo Backend API.
---

## Base URL

All endpoints are prefixed with:

```
/api/v1
```

Example: `https://api.yourdomain.com/api/v1/auth/login`

---

## Authentication

Most endpoints require a valid **JWT Bearer token** obtained from `POST /api/v1/auth/login`.

Include it in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Access tokens expire after **30 minutes** by default. Use `POST /api/v1/auth/refresh` to get a new pair of tokens.

---

## Roles & Permissions

| Role | Abbreviation | Description |
|------|-------------|-------------|
| Admin | `ADMIN` | Full unrestricted access |
| Seller | `VENDEDOR` | Can manage clients, issue and view policies, create payments |
| Client | *(none)* | Can only access the `/portal` routes for their own data |

---

## Response Format

Successful responses return JSON. The exact shape depends on each endpoint and is described in the individual reference pages.

### Pagination

Endpoints that return paginated data (e.g. Audit) include these fields:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| `400` | Bad Request — validation error or malformed payload |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — authenticated but insufficient role |
| `404` | Not Found — resource does not exist |
| `409` | Conflict — duplicate resource or constraint violation |
| `422` | Unprocessable Entity — Pydantic validation failure |
| `500` | Internal Server Error |

Error responses follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

For `422` errors the `detail` field is an array of validation error objects as defined by FastAPI / Pydantic.

---

## Health Check

```http
GET /api/v1/health
```

Returns the status of the database and Redis connections. No authentication required.

**Response:**

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok"
}
```

---

## API Modules

| Module | Base Path | Description |
|--------|-----------|-------------|
| [Authentication](/reference/auth/) | `/api/v1/auth` | Register, login, token management, roles |
| [Plans](/reference/plans/) | `/api/v1/plans` | Funeral plan CRUD and price calculation |
| [Emission](/reference/emission/) | `/api/v1/emission` | Client registration, policy issuance, PDF |
| [Payments](/reference/payments/) | `/api/v1/payments` | Stripe payments, subscriptions, transactions |
| [Audit](/reference/audit/) | `/api/v1/audit` | Paginated system-wide audit log |
| [Portal](/reference/portal/) | `/api/v1/portal` | Self-service portal for clients |
