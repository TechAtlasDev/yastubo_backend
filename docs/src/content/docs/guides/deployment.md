---
title: Despliegue en VPS
description: Guía paso a paso para desplegar Yastubo Backend en un servidor de producción/staging.
---

Esta guía cubre el despliegue completo de Yastubo Backend en un VPS Ubuntu 22.04 usando Docker Compose.

## Requisitos del servidor

| Componente | Mínimo recomendado |
|------------|-------------------|
| OS | Ubuntu 22.04 LTS |
| RAM | 2 GB |
| CPU | 2 vCPUs |
| Disco | 20 GB SSD |
| Puertos abiertos | 22 (SSH), 80, 443, 8000 |

---

## 1. Preparar el servidor

```bash
# Actualizar paquetes del sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

---

## 2. Clonar el repositorio

```bash
git clone https://github.com/TechAtlasDev/yastubo_backend.git
cd yastubo_backend
```

---

## 3. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

Variables **obligatorias** para que el sistema arranque:

```env
APP_ENV="staging"
DEBUG=False

# Base de datos — usa el nombre del servicio Docker, no localhost
DATABASE_URL="postgresql+asyncpg://user:password@postgres:5432/yastubo"
DATABASE_URL_SYNC="postgresql+psycopg2://user:password@postgres:5432/yastubo"
POSTGRES_DB="yastubo"
POSTGRES_USER="user"
POSTGRES_PASSWORD="tu_password_seguro"

# Redis — usa el nombre del servicio Docker
REDIS_URL="redis://redis:6379"

# Seguridad
SECRET_KEY="genera-uno-con: python -c 'import secrets; print(secrets.token_hex(32))'"

# Stripe (modo sandbox)
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

FRONTEND_URL="https://tu-dominio.com"
BACKEND_CORS_ORIGINS=["https://tu-dominio.com"]
```

:::caution[Importante]
Para staging, deja `NOTIFICATIONS_ENABLED=False`, `WHATSAPP_ENABLED=False` y `CRM_ENABLED=False` hasta tener las credenciales reales del equipo Yastubo.
:::

---

## 4. Levantar los servicios

```bash
# Construir imágenes y levantar todos los servicios
docker compose up --build -d

# Verificar que todos los contenedores están corriendo
docker compose ps
```

Deberías ver estos servicios en estado `Up`:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `app` | 8000 | API FastAPI |
| `postgres` | 5432 | Base de datos |
| `redis` | 6379 | Caché y sesiones |
| `worker` | — | ARQ background jobs |

---

## 5. Ejecutar migraciones y seed inicial

```bash
# Aplicar todas las migraciones de base de datos
docker compose exec app alembic upgrade head

# Crear roles iniciales (ADMIN, VENDEDOR, CLIENTE)
docker compose exec app uv run python scripts/seed_roles.py
```

---

## 6. Verificar que el sistema funciona

```bash
# Health check
curl http://localhost:8000/api/v1/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "db": "ok",
  "redis": "ok",
  "env": "staging",
  "version": "0.2.0"
}
```

La documentación interactiva Swagger estará disponible en:

```
http://tu-ip-o-dominio:8000/docs
```

---

## 7. Configurar Nginx como reverse proxy (opcional pero recomendado)

```bash
sudo apt install nginx -y
```

Crear archivo de configuración:

```bash
sudo nano /etc/nginx/sites-available/yastubo
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support (Voice AI)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/yastubo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 8. Configurar webhooks de Stripe

Una vez el servidor esté público, registra la URL del webhook en el dashboard de Stripe:

```
https://tu-dominio.com/api/v1/payments/webhook
```

Eventos a suscribir:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.subscription.deleted`

Actualiza `STRIPE_WEBHOOK_SECRET` en tu `.env` con el secreto generado y reinicia:

```bash
docker compose restart app worker
```

---

## Comandos útiles de operación

```bash
# Ver logs en tiempo real
docker compose logs -f app

# Ver logs del worker (tareas programadas)
docker compose logs -f worker

# Reiniciar solo la app (sin bajar DB/Redis)
docker compose restart app

# Detener todo
docker compose down

# Detener y eliminar volúmenes (¡borra la DB!)
docker compose down -v
```

---

## Solución de problemas comunes

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| `app` no arranca | DB no lista | Esperar healthcheck: `docker compose logs postgres` |
| `alembic upgrade head` falla | Variables de entorno incorrectas | Verificar `DATABASE_URL_SYNC` en `.env` |
| Webhook Stripe retorna 400 | Secret incorrecto | Revisar `STRIPE_WEBHOOK_SECRET` |
| Emails no se envían | `NOTIFICATIONS_ENABLED=False` | Activar y configurar `SENDGRID_API_KEY` |
