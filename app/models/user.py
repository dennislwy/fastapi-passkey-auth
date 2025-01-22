from typing import Optional, List
from uuid import uuid4
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, GUID

class User(Base):
    """User model for storing user information.

    Attributes:
        email: User's email address
        hashed_password: Hashed password for traditional login
        full_name: User's full name
        is_active: Flag indicating if the user is active
        is_verified: Flag indicating if the user is verified
        is_superuser: Flag indicating if the user is a superuser
    """
    __tablename__ = "users"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=str(uuid4()), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    credentials: Mapped[List["WebAuthnCredential"]] = relationship(
        back_populates="users", cascade="all, delete-orphan"
    )
