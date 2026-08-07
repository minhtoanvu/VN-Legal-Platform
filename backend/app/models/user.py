"""
Models cho User và Organization.

Bảng:
- organizations : Công ty / tổ chức (cho gói Enterprise)
- users         : Tài khoản người dùng với RBAC
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # RBAC roles: user / enterprise / admin
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Enterprise link
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", back_populates="users"
    )
    collections: Mapped[List["Collection"]] = relationship(  # type: ignore[name-defined]
        "Collection", back_populates="owner", cascade="all, delete-orphan"
    )
    notes: Mapped[List["Note"]] = relationship(  # type: ignore[name-defined]
        "Note", back_populates="user", cascade="all, delete-orphan"
    )
    query_logs: Mapped[List["QueryLog"]] = relationship(  # type: ignore[name-defined]
        "QueryLog", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"

    @property
    def is_enterprise(self) -> bool:
        return self.role in ("enterprise", "admin")

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
