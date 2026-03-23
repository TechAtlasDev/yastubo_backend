---
title: Audit
description: Paginated system-wide audit log — admin access only.
---

Base path: `/api/v1/audit`

---

## GET `/audit`

Retrieve a paginated list of audit log entries. Every action performed in the system (policy transitions, payments, role assignments, etc.) is recorded here.

**Authentication:** Required — `ADMIN` role only

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | UUID | — | Filter by the user who performed the action |
| `action` | string | — | Filter by action name (e.g. `"issue_policy"`, `"login"`) |
| `entity` | string | — | Filter by entity type (e.g. `"Policy"`, `"User"`) |
| `entity_id` | UUID | — | Filter by the specific entity affected |
| `date_from` | datetime (ISO 8601) | — | Start of date range |
| `date_to` | datetime (ISO 8601) | — | End of date range |
| `page` | integer (≥1) | `1` | Page number |
| `page_size` | integer (1–100) | `50` | Number of results per page |

**Example request:**

```http
GET /api/v1/audit?entity=Policy&action=status_transition&page=1&page_size=20
Authorization: Bearer <admin_token>
```

**Response `200 OK`:**

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "status_transition",
      "entity": "Policy",
      "entity_id": "661f9511-f3ac-52e5-b827-557766551111",
      "user_id": "772a0622-e4bd-63f6-c938-668877662222",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 ...",
      "old_values": { "status": "PENDING_PAYMENT" },
      "new_values": { "status": "ACTIVE" },
      "extra": null,
      "details": "Payment confirmed",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

## Schemas

### PaginatedAuditResponse

| Field | Type | Description |
|-------|------|-------------|
| `items` | AuditLogResponse[] | List of audit entries for the current page |
| `total` | integer | Total number of matching entries |
| `page` | integer | Current page number |
| `page_size` | integer | Number of entries per page |

### AuditLogResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Audit log entry identifier |
| `action` | string | Name of the action performed |
| `entity` | string | Entity type affected (e.g. `"Policy"`, `"User"`, `"Plan"`) |
| `entity_id` | string \| null | Identifier of the affected entity |
| `user_id` | UUID \| null | ID of the user who performed the action |
| `ip_address` | string \| null | IP address of the request |
| `user_agent` | string \| null | Browser / client user agent |
| `old_values` | object \| null | Previous state before the action |
| `new_values` | object \| null | New state after the action |
| `extra` | object \| null | Additional context-specific metadata |
| `details` | string \| null | Human-readable description |
| `created_at` | datetime | Timestamp of the audit event |
