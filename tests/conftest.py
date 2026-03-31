import pytest
import asyncio
import uuid
import sqlite3
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fakeredis import FakeAsyncRedis
from datetime import date, timedelta

from app.main import app as fastapi_app
from app.core.database import Base, get_db
from app.core.redis import get_redis
from app.modules.auth.models import User, Role, UserRole
from app.modules.auth.security import get_password_hash, create_access_token
from app.modules.plans.models import Coverage
from app.modules.organizations.models import Company, CompanyUser

# Register UUID adapter and converter for SQLite
sqlite3.register_adapter(uuid.UUID, lambda u: u.hex)
sqlite3.register_converter("GUID", lambda b: uuid.UUID(b.decode()))

# Use SQLite in-memory for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
def patch_session_local(db_session, monkeypatch):
    from app.modules.payments import router
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def mock_session_local():
        yield db_session

    monkeypatch.setattr(router, "SessionLocal", mock_session_local)


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await test_engine.connect()
    transaction = await connection.begin()

    AsyncSessionLocal = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = AsyncSessionLocal()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def redis_client():
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.close()


@pytest.fixture(scope="session")
def app():
    return fastapi_app


@pytest.fixture
async def client(db_session, redis_client) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    async def override_get_redis():
        yield redis_client

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()


# Shared Auth Fixtures
@pytest.fixture
async def roles(db_session):
    role_defs = [
        {"name": "ADMIN", "scope": "staff"},
        {"name": "VENDEDOR", "scope": "staff"},
        {"name": "CLIENTE", "scope": "customer"},
    ]
    roles_dict = {}
    from sqlalchemy import select

    for rdef in role_defs:
        # Check if exists
        res = await db_session.execute(select(Role).where(Role.name == rdef["name"]))
        role = res.scalar_one_or_none()
        if not role:
            role = Role(name=rdef["name"], scope=rdef["scope"], guard_name="web")
            db_session.add(role)
            await db_session.flush()
        roles_dict[rdef["name"]] = role
    return roles_dict


@pytest.fixture
async def default_company(db_session):
    from sqlalchemy import select

    res = await db_session.execute(
        select(Company).where(Company.short_code == "yastubo-default")
    )
    company = res.scalar_one_or_none()
    if not company:
        company = Company(name="Yastubo Default", short_code="yastubo-default")
        db_session.add(company)
        await db_session.commit()
    return company


@pytest.fixture
async def admin_user(db_session, roles, default_company):
    from sqlalchemy import select

    res = await db_session.execute(
        select(User).where(User.email == "admin@yastubo.com")
    )
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            email="admin@yastubo.com",
            hashed_password=get_password_hash("password123"),
            full_name="Admin User",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        user_role = UserRole(user_id=user.id, role_id=roles["ADMIN"].id)
        db_session.add(user_role)
        from app.modules.auth.models import PasswordHistory

        db_session.add(
            PasswordHistory(user_id=user.id, password_hash=user.hashed_password)
        )

    # Always ensure company link
    ws_res = await db_session.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == user.id,
            CompanyUser.company_id == default_company.id,
        )
    )
    if not ws_res.scalar_one_or_none():
        user_ws = CompanyUser(user_id=user.id, company_id=default_company.id)
        db_session.add(user_ws)

    await db_session.commit()
    await db_session.refresh(user, ["roles", "companies"])
    return user


@pytest.fixture
async def client_user(db_session, roles, default_company):
    from sqlalchemy import select

    res = await db_session.execute(
        select(User).where(User.email == "client@yastubo.com")
    )
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            email="client@yastubo.com",
            hashed_password=get_password_hash("password123"),
            full_name="Client User",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        user_role = UserRole(user_id=user.id, role_id=roles["CLIENTE"].id)
        db_session.add(user_role)
        from app.modules.auth.models import PasswordHistory

        db_session.add(
            PasswordHistory(user_id=user.id, password_hash=user.hashed_password)
        )

    # Always ensure company link
    ws_res = await db_session.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == user.id,
            CompanyUser.company_id == default_company.id,
        )
    )
    if not ws_res.scalar_one_or_none():
        user_ws = CompanyUser(user_id=user.id, company_id=default_company.id)
        db_session.add(user_ws)

    await db_session.commit()
    await db_session.refresh(user, ["roles", "companies"])
    return user


# Shared Plan Fixtures
@pytest.fixture
async def coverage(db_session):
    coverage = Coverage(
        name="Repatriación",
        description="Traslado de restos",
    )
    db_session.add(coverage)
    await db_session.commit()
    await db_session.refresh(coverage)
    return coverage


@pytest.fixture
def product_payload(coverage):
    return {
        "name": "Asistencia Funeraria",
        "description": "Producto base de repatriación",
        "product_type": "repatriation",
        "is_active": True,
        "plans": [
            {
                "name": "Plan Familiar Latam",
                "description": "Cobertura completa para familias",
                "is_active": True,
                "versions": [
                    {
                        "version_number": 1,
                        "cost_price": 40.00,
                        "public_price": 50.00,
                        "currency": "USD",
                        "max_entry_age": 65,
                        "max_renewal_age": 85,
                        "wtime_suicide": 365,
                        "wtime_preexisting": 180,
                        "wtime_accident": 0,
                        "age_surcharges": [
                            {"min_age": 0, "max_age": 30, "surcharge_percentage": 0},
                            {"min_age": 31, "max_age": 65, "surcharge_percentage": 20},
                        ],
                        "countries": [
                            {
                                "country_code": "CO",
                                "country_name": "Colombia",
                                "price_override": None,
                                "is_available": True,
                            },
                            {
                                "country_code": "MX",
                                "country_name": "México",
                                "price_override": 60.00,
                                "is_available": True,
                            },
                        ],
                        "coverages": [
                            {
                                "coverage_id": str(coverage.id),
                                "value_int": 5000,
                                "is_included": True,
                            }
                        ],
                        "repatriation_countries": [
                            {"country_code": "CO", "country_name": "Colombia"},
                            {"country_code": "MX", "country_name": "México"},
                        ],
                    }
                ],
            }
        ],
    }


@pytest.fixture
async def created_product(client: AsyncClient, admin_user, product_payload):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/products/", json=product_payload, headers=headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def created_plan(created_product):
    return created_product["plans"][0]


# Shared Emission Fixtures
@pytest.fixture
async def test_client(client: AsyncClient, admin_user):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": f"juan.{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+573001234567",
        "birth_date": str(date.today() - timedelta(days=30 * 365)),  # 30 years old
        "nationality": "CO",
        "country_of_residence": "MX",
        "document_type": "PASSPORT",
        "document_number": "P1234567",
        "address": "Calle 123, Ciudad de México",
    }
    response = await client.post(
        "/api/v1/emission/clients", json=payload, headers=headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def emission_request_payload(test_client, created_plan):
    return {
        "client_id": test_client["id"],
        "plan_id": created_plan["id"],
        "plan_version_id": created_plan["versions"][0]["id"],
        "country_code": "MX",
        "start_date": str(date.today() + timedelta(days=1)),
        "notes": "Prueba de emisión",
    }


@pytest.fixture
async def issued_policy(client: AsyncClient, admin_user, emission_request_payload):
    token = create_access_token(
        {"sub": str(admin_user.id), "roles": ["ADMIN"], "type": "access"}
    )
    headers = {"Authorization": f"Bearer {token}"}
    # Mock weasyprint PDF generation
    from unittest.mock import patch

    with patch(
        "app.modules.emission.pdf_generator.generate_contract_pdf",
        return_value=b"%PDF-1.4 mock content",
    ):
        response = await client.post(
            "/api/v1/emission/issue", json=emission_request_payload, headers=headers
        )
        assert response.status_code == 201
        return response.json()
