import uuid
from typing import Callable, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.security import decode_token
from app.modules.auth.service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = uuid.UUID(user_id_str)
    user = await get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


async def get_current_company_id(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    company_id: Optional[uuid.UUID] = Header(None, alias="X-Company-Id"),
) -> uuid.UUID:
    """
    Get the current company ID for the user.
    If multiple companies exist, the X-Company-Id header must be provided.
    """
    from app.modules.organizations.models import Company

    if company_id:
        # Check if user belongs to this company
        if any(ws.id == company_id for ws in user.companies):
            return company_id
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this company",
        )

    if len(user.companies) == 1:
        return user.companies[0].id

    if len(user.companies) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Multiple companies found. Please specify X-Company-Id header.",
        )

    # Fallback: if user is ADMIN but has no company, use the first one available
    user_roles = [role.name for role in user.roles]
    if "ADMIN" in user_roles:
        from sqlalchemy import select

        res = await db.execute(select(Company).limit(1))
        first_company = res.scalar_one_or_none()
        if first_company:
            return first_company.id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not assigned to any company",
    )


def require_role(*roles: str) -> Callable:
    def role_checker(user: User = Depends(get_current_user)):
        user_roles = [role.name for role in user.roles]
        if not any(role in user_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions to perform this action",
            )
        return user

    return role_checker


def require_scope(scope: str) -> Callable:
    def scope_checker(user: User = Depends(get_current_user)):
        # User has the scope if at least one of their roles has that scope
        if not any(role.scope == scope for role in user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You must have {scope} scope to access this.",
            )
        return user

    return scope_checker
