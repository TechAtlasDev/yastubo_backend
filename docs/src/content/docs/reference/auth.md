---
title: Authentication
description: User registration, login, token management, and role assignment endpoints.
---

Base path: `/api/v1/auth`

---

## POST `/auth/register`

Register a new user account.

**Authentication:** Not required

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | ✅ | Unique email address |
| `password` | string | ✅ | Minimum 8 characters |
| `full_name` | string | ✅ | User's full name |
| `phone` | string | ❌ | Phone number |

```json
{
  "email": "user@example.com",
  "password": "securepass",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

**Response `201 Created`:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "is_active": true,
  "roles": [],
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## POST `/auth/login`

Authenticate a user and receive JWT tokens.

**Authentication:** Not required

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | ✅ | Registered email |
| `password` | string | ✅ | Account password |

```json
{
  "email": "user@example.com",
  "password": "securepass"
}
```

**Response `200 OK`:**

```json
{
  "access_token": "<JWT>",
  "refresh_token": "<JWT>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

| Field | Description |
|-------|-------------|
| `access_token` | Short-lived JWT (default: 30 min) used in `Authorization: Bearer` header |
| `refresh_token` | Long-lived JWT (default: 7 days) used only to get a new token pair |
| `expires_in` | Access token lifetime in seconds |

---

## POST `/auth/refresh`

Exchange a valid refresh token for a new access/refresh token pair.

**Authentication:** Not required (refresh token is the credential)

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `refresh_token` | string | ✅ | Valid refresh token |

```json
{
  "refresh_token": "<refresh_token>"
}
```

**Response `200 OK`:** Same shape as the login response.

---

## POST `/auth/logout`

Invalidate the current user's tokens (stored in Redis).

**Authentication:** Required (any authenticated user)

**Request body:** None

**Response `204 No Content`**

---

## POST `/auth/roles/assign`

Assign a role to a user.

**Authentication:** Required — `ADMIN` role

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | ✅ | ID of the user to update |
| `role_name` | string | ✅ | Role to assign (`ADMIN`, `VENDEDOR`, …) |

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role_name": "VENDEDOR"
}
```

**Response `200 OK`:** Updated `UserResponse` object.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": null,
  "is_active": true,
  "roles": ["VENDEDOR"],
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## GET `/auth/me`

Retrieve the profile of the currently authenticated user.

**Authentication:** Required (any authenticated user)

**Response `200 OK`:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "is_active": true,
  "roles": ["ADMIN"],
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## Schemas

### UserResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique user identifier |
| `email` | string | Email address |
| `full_name` | string | Full name |
| `phone` | string \| null | Phone number |
| `is_active` | boolean | Whether the account is active |
| `roles` | string[] | List of role names assigned to the user |
| `created_at` | datetime (ISO 8601) | Account creation timestamp |

### TokenResponse

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token |
| `refresh_token` | string | JWT refresh token |
| `token_type` | string | Always `"bearer"` |
| `expires_in` | integer | Access token TTL in seconds |
