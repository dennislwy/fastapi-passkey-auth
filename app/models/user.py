from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUID

class User(Base):
    """User model for storing user information.

    Attributes:
        email: User's email address
        password_hash: Hashed password for traditional login
        full_name: User's full name
        authenticators: List of associated WebAuthn authenticators
        is_active: Flag indicating if the user is active
        last_login_at: Timestamp of the user last login time
    """
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    is_active = mapped_column(Boolean, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    authenticators: Mapped[List["Authenticator"]] = relationship(
        back_populates="users",
        cascade="all, delete-orphan"
        )
