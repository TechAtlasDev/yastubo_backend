from sqlalchemy import text
import pytest

# test 1: la app levanta y el health check responde 200
async def test_health_check_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# test 2: la conexión a la base de datos de test funciona
async def test_database_connection(db_session):
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

# test 3: la conexión a Redis funciona
async def test_redis_connection(redis_client):
    await redis_client.set("test_key", "test_value")
    value = await redis_client.get("test_key")
    assert value == b"test_value"
