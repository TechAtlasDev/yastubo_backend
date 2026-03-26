import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID
from app.core.database import Base

class Workspace(BaseModel):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata for Resellers
    is_reseller: Mapped[bool] = mapped_column(Boolean, default=False)
    stripe_connect_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    users: Mapped[List["User"]] = relationship(
        secondary="user_workspaces",
        back_populates="workspaces"
    )

class UserWorkspace(Base):
    __tablename__ = "user_workspaces"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
