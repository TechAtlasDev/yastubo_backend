---
title: Getting Started
description: Set up and start using the Yastubo Backend API.
---

## Requirements

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| MySQL | 8.0+ |
| Redis | 6.0+ |
| Docker / Docker Compose | optional but recommended |

---

## Running Locally with Docker Compose

The easiest way to spin up the full stack (API, MySQL, Redis) is with Docker Compose.

```bash
# Clone the repository
git clone https://github.com/TechAtlasDev/yastubo_backend.git
cd yastubo_backend

# Copy environment configuration
cp .env.example .env
# Edit .env with your Stripe keys, database credentials, etc.

# Start all services
docker compose up --build
```

The API will be available at `http://localhost:8000`.

---

## Running Without Docker

```bash
# Install Python dependencies
pip install -e .

# Apply database migrations
alembic upgrade head

# Seed initial roles
python scripts/seed_roles.py

# Start the API server
uvicorn app.main:app --reload
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the required values:

| Variable | Description |
|----------|-------------|
| `APP_ENV` | `development`, `staging`, or `production` |
| `SECRET_KEY` | Secret used for JWT signing |
| `DATABASE_URL` | Async MySQL connection string (`mysql+aiomysql://...`) |
| `REDIS_URL` | Redis connection string (default: `redis://localhost:6379`) |
| `STRIPE_SECRET_KEY` | Stripe secret API key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `STRIPE_CONNECT_CLIENT_ID` | Stripe Connect application client ID |
| `SENDGRID_API_KEY` | SendGrid key for email notifications |
| `FRONTEND_URL` | URL of the frontend app (used for CORS and redirects) |

---

## Authentication Flow

All protected endpoints require a **Bearer JWT** in the `Authorization` header.

### 1. Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

### 2. Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass"
}
```

**Response:**

```json
{
  "access_token": "<JWT>",
  "refresh_token": "<JWT>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Use the token

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### 4. Refresh when expired

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

---

## User Roles

| Role | Description |
|------|-------------|
| `ADMIN` | Full access to all endpoints |
| `VENDEDOR` | Can register clients, issue and list policies, and create payments |
| *(no role)* | Can access the self-service portal (`/api/v1/portal`) |

Roles are assigned by an admin:

```http
POST /api/v1/auth/roles/assign
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_id": "<uuid>",
  "role_name": "VENDEDOR"
}
```

---

## Interactive API Docs (Swagger)

Once the server is running, open `http://localhost:8000/docs` for the interactive Swagger UI, or `http://localhost:8000/redoc` for ReDoc.
