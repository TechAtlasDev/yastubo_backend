import pytest
import uuid
from httpx import AsyncClient
from app.modules.auth.security import create_access_token, decode_token

@pytest.mark.asyncio
async def test_register_new_user_returns_201(client: AsyncClient, roles):
    payload = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
        "phone": "123456789"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "CLIENTE" in data["roles"]

@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient, client_user):
    payload = {
        "email": client_user.email,
        "password": "password123",
        "full_name": "Duplicate User"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_register_assigns_cliente_role_by_default(client: AsyncClient, roles):
    payload = {
        "email": "another@example.com",
        "password": "password123",
        "full_name": "Another User"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert "CLIENTE" in response.json()["roles"]

@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens(client: AsyncClient, client_user):
    payload = {
        "email": client_user.email,
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient, client_user):
    payload = {
        "email": client_user.email,
        "password": "wrongpassword"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_email_returns_401(client: AsyncClient, db_session):
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_access_token_payload_contains_roles(client_user):
    token_data = {
        "sub": str(client_user.id),
        "email": client_user.email,
        "roles": [role.name for role in client_user.roles]
    }
    token = create_access_token(token_data)
    payload = decode_token(token)
    assert "roles" in payload
    assert "CLIENTE" in payload["roles"]

@pytest.mark.asyncio
async def test_refresh_tokens_returns_new_pair(client: AsyncClient, client_user, redis_client):
    # Setup: login to get a refresh token
    login_payload = {"email": client_user.email, "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_res.json()["refresh_token"]
    
    # Mock redis storage if needed (but service already does it)
    # The fixture redis_client is used by the app because of dependency injection or global client
    # In my app/core/redis.py it uses a global redis_client. 
    # To test properly we should ideally override the redis_client dependency.
    
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_logout_invalidates_refresh_token(client: AsyncClient, client_user, redis_client):
    # Login
    login_payload = {"email": client_user.email, "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    tokens = login_res.json()
    
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Logout
    logout_res = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 204
    
    # Try refresh
    refresh_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_res.status_code == 401

@pytest.mark.asyncio
async def test_get_me_returns_current_user(client: AsyncClient, client_user):
    token = create_access_token({
        "sub": str(client_user.id),
        "email": client_user.email,
        "roles": ["CLIENTE"],
        "type": "access"
    })
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == client_user.email

@pytest.mark.asyncio
async def test_assign_role_by_admin_succeeds(client: AsyncClient, admin_user, client_user, roles):
    token = create_access_token({
        "sub": str(admin_user.id),
        "email": admin_user.email,
        "roles": ["ADMIN"],
        "type": "access"
    })
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": str(client_user.id),
        "role_name": "VENDEDOR"
    }
    response = await client.post("/api/v1/auth/roles/assign", json=payload, headers=headers)
    assert response.status_code == 200
    assert "VENDEDOR" in response.json()["roles"]

@pytest.mark.asyncio
async def test_assign_role_by_non_admin_returns_403(client: AsyncClient, client_user, roles):
    token = create_access_token({
        "sub": str(client_user.id),
        "email": client_user.email,
        "roles": ["CLIENTE"],
        "type": "access"
    })
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": str(client_user.id),
        "role_name": "ADMIN"
    }
    response = await client.post("/api/v1/auth/roles/assign", json=payload, headers=headers)
    assert response.status_code == 403
