import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # in seconds

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: Optional[str]
    is_active: bool
    roles: List[str] = []
    created_at: datetime

    @classmethod
    def from_orm_with_roles(cls, user):
        roles = [role.name for role in user.roles]
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            roles=roles,
            created_at=user.created_at
        )

class RefreshRequest(BaseModel):
    refresh_token: str

class RoleAssign(BaseModel):
    user_id: uuid.UUID
    role_name: str
