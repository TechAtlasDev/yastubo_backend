import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.config import settings
from app.modules.auth.models import User, Role, UserRole
from app.modules.auth.schemas import UserRegister, UserLogin, TokenResponse, RoleAssign
from app.modules.auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.modules.audit.decorator import audited

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email).options(selectinload(User.roles))
    )
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.roles))
    )
    return result.scalar_one_or_none()

@audited(action="USER_REGISTERED", entity="User")
async def register_user(db: AsyncSession, data: UserRegister) -> User:
    # Check if email exists
    existing_user = await get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(data.password)
    user = User(
        email=data.email,
        hashed_password=hashed_password,
        full_name=data.full_name,
        phone=data.phone,
        is_active=True,
    )
    db.add(user)
    await db.flush() # To get user.id

    # Assign CLIENTE role by default
    role_result = await db.execute(select(Role).where(Role.name == "CLIENTE"))
    cliente_role = role_result.scalar_one_or_none()
    if cliente_role:
        user_role = UserRole(user_id=user.id, role_id=cliente_role.id)
        db.add(user_role)
    
    await db.commit()
    await db.refresh(user, ["roles"])
    return user

async def login_user(db: AsyncSession, redis: Redis, data: UserLogin) -> TokenResponse:
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Update last login
    user.last_login = datetime.now()
    await db.commit()

    return await generate_tokens(redis, user)

async def generate_tokens(redis: Redis, user: User) -> TokenResponse:
    roles = [role.name for role in user.roles]
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "roles": roles
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    # Store refresh token in Redis
    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis.set(f"refresh:{user.id}", refresh_token, ex=ttl)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

async def refresh_tokens(db: AsyncSession, redis: Redis, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    user_id = uuid.UUID(user_id_str)
    
    # Verify in Redis
    stored_token = await redis.get(f"refresh:{user_id}")
    if not stored_token or stored_token != refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or expired")
    
    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    
    return await generate_tokens(redis, user)

async def logout_user(redis: Redis, user_id: uuid.UUID):
    await redis.delete(f"refresh:{user_id}")

@audited(action="ROLE_ASSIGNED", entity="User")
async def assign_role(db: AsyncSession, data: RoleAssign, assigned_by: uuid.UUID) -> User:
    # Check role exists
    role_result = await db.execute(select(Role).where(Role.name == data.role_name))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    # Check user exists
    user = await get_user_by_id(db, data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if already assigned
    existing_role = next((r for r in user.roles if r.name == data.role_name), None)
    if not existing_role:
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            assigned_by=assigned_by
        )
        db.add(user_role)
        
        await db.commit()
        await db.refresh(user, ["roles"])
    
    return user
