import pytest
import pytest_asyncio
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.auth.models import User, Role, UserRole
from app.modules.auth.security import get_password_hash, create_access_token
from app.modules.emission.models import Client, Policy
from app.modules.emission.state_machine import PolicyStatus

@pytest_asyncio.fixture
async def client_user_with_profile(db_session: AsyncSession):
    # 1. Create User
    email = f"client_{uuid.uuid4().hex[:6]}@example.com"
    user = User(
        email=email,
        hashed_password=get_password_hash("password123"),
        full_name="Test Portal Client",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    
    # 2. Ensure CLIENTE role exists
    res = await db_session.execute(select(Role).where(Role.name == "CLIENTE"))
    role = res.scalar_one_or_none()
    if not role:
        role = Role(name="CLIENTE")
        db_session.add(role)
        await db_session.flush()

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    
    # 3. Create Client profile
    client_profile = Client(
        email=email,
        first_name="Test",
        last_name="Portal",
        birth_date=date(1990, 1, 1),
        phone="+123456789",
        address="123 Test St",
        nationality="US",
        country_of_residence="US",
        document_type="PASSPORT",
        document_number="P1234567",
        created_by=user.id
    )
    db_session.add(client_profile)
    await db_session.commit()
    await db_session.refresh(user, ["roles"])
    await db_session.refresh(client_profile)
    return user, client_profile

@pytest_asyncio.fixture
async def client_user_token(client_user_with_profile):
    user, _ = client_user_with_profile
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "roles": ["CLIENTE"],
        "type": "access"
    }
    return create_access_token(token_data)

@pytest_asyncio.fixture
async def active_policy_for_client(db_session: AsyncSession, client_user_with_profile):
    user, client = client_user_with_profile
    policy = Policy(
        policy_number=f"POL-{uuid.uuid4().hex[:6].upper()}",
        client_id=client.id,
        plan_id=uuid.uuid4(), # Dummy ID
        plan_version_snapshot={"name": "Test Plan"},
        status=PolicyStatus.ACTIVE,
        base_price=100.0,
        surcharge_amount=0.0,
        final_price=100.0,
        currency="USD",
        country_code="US",
        insured_age=34,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        issued_by=user.id
    )
    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy
