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


async def get_current_workspace_id(
    user: User = Depends(get_current_user),
    workspace_id: Optional[uuid.UUID] = Header(None, alias="X-Workspace-Id"),
) -> uuid.UUID:
    """
    Get the current workspace ID for the user.
    If multiple workspaces exist, the X-Workspace-Id header must be provided.
    """
    if workspace_id:
        # Check if user belongs to this workspace
        if any(ws.id == workspace_id for ws in user.workspaces):
            return workspace_id
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace",
        )

    if len(user.workspaces) == 1:
        return user.workspaces[0].id

    if len(user.workspaces) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Multiple workspaces found. Please specify X-Workspace-Id header.",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not assigned to any workspace",
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
