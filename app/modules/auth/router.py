from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.modules.auth.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshRequest,
    RoleAssign,
    PasswordChange,
)
from app.modules.auth import service
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await service.register_user(db, data)
    return UserResponse.from_orm_with_roles(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await service.login_user(db, redis, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await service.refresh_tokens(db, redis, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: User = Depends(get_current_user), redis: Redis = Depends(get_redis)
):
    await service.logout_user(redis, user.id)
    return None


@router.post("/roles/assign", response_model=UserResponse)
async def assign_role(
    data: RoleAssign,
    admin_user: User = Depends(require_role("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    user = await service.assign_role(db, data, admin_user.id)
    return UserResponse.from_orm_with_roles(user)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse.from_orm_with_roles(user)


@router.put("/password")
async def change_password(
    data: PasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.change_password(db, user, data)
