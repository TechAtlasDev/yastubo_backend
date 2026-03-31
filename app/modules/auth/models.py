import uuid
from datetime import datetime, date
import enum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    ForeignKey,
    Boolean,
    DateTime,
    Table,
    Column,
    func,
    Text,
    Date,
    Enum,
    BigInteger,
    UniqueConstraint,
    JSON,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.base_model import BaseModel, GUID
from app.core.database import Base

# Ensure related models are registered in the metadata
import app.modules.organizations.models  # noqa: F401

if TYPE_CHECKING:
    from app.modules.organizations.models import Company, BusinessUnit

# Many-to-Many Role <-> Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id", GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        GUID(),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(BaseModel):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint(
            "name", "guard_name", name="permissions_name_guard_name_unique"
        ),
    )

    name: Mapped[str] = mapped_column(String(191), nullable=False)
    guard_name: Mapped[str] = mapped_column(String(191), nullable=False, default="web")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )


class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("name", "guard_name", name="roles_name_guard_name_unique"),
    )

    name: Mapped[str] = mapped_column(String(191), nullable=False)
    guard_name: Mapped[str] = mapped_column(String(191), nullable=False, default="web")
    scope: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    level: Mapped[int] = mapped_column(default=0, nullable=False)
    label: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Keeping description for backwards compatibility
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permissions, back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        primaryjoin="Role.id == user_roles.c.role_id",
        secondaryjoin="User.id == user_roles.c.user_id",
        overlaps="roles,users",
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    assigned_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=True
    )


class PasswordHistory(Base):
    __tablename__ = "password_histories"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(191), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class PreferredLanguageEnum(str, enum.Enum):
    es = "es"
    en = "en"


class ContactViaEnum(str, enum.Enum):
    email = "email"
    whatsapp = "whatsapp"
    sms = "sms"


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    mobile_e164: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    alt_email: Mapped[Optional[str]] = mapped_column(String(190), nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    doc_number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(
        Enum(GenderEnum), nullable=True
    )
    preferred_language: Mapped[Optional[PreferredLanguageEnum]] = mapped_column(
        Enum(PreferredLanguageEnum), nullable=True, default=PreferredLanguageEnum.es
    )
    contact_via: Mapped[Optional[ContactViaEnum]] = mapped_column(
        Enum(ContactViaEnum), nullable=True, default=ContactViaEnum.email
    )
    residence_address_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    home_address_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_admin: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="customer_profile")


class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    internal_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes_admin: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="staff_profile")


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    roles: Mapped[List["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        primaryjoin="User.id == user_roles.c.user_id",
        secondaryjoin="Role.id == user_roles.c.role_id",
        overlaps="roles,users",
    )

    companies: Mapped[List["Company"]] = relationship(
        secondary="company_user", back_populates="users"
    )

    business_units: Mapped[List["BusinessUnit"]] = relationship(
        secondary="memberships_business_unit", back_populates="users"
    )

    customer_profile: Mapped[Optional["CustomerProfile"]] = relationship(
        "CustomerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    staff_profile: Mapped[Optional["StaffProfile"]] = relationship(
        "StaffProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    password_histories: Mapped[List["PasswordHistory"]] = relationship(
        "PasswordHistory",
        cascade="all, delete-orphan",
        order_by="desc(PasswordHistory.created_at)",
    )
