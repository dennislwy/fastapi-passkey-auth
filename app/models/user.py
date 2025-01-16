from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    """User model for storing user information.

    Attributes:
        email: User's email address
        password_hash: Hashed password for traditional login
        full_name: User's full name
        authenticators: List of associated WebAuthn authenticators
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    is_active = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    authenticators: Mapped[List["Authenticator"]] = relationship(
        back_populates="users",
        cascade="all, delete-orphan"
        )

class Authenticator(Base):
    """WebAuthn authenticator model.

    Attributes:
        credential_id: Base64 encoded credential ID
        public_key: Base64 encoded public key
        sign_count: Number of times the authenticator has been used
        user_id: ID of the associated user
        user: Reference to the associated user
    """
    __tablename__ = "authenticators"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    credential_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    public_key: Mapped[str] = mapped_column(String(255))
    sign_count: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship(back_populates="authenticators")

    def get_credential_data(self):
        """Convert stored credential data to dictionary format."""
        return {
            "credential_id": self.credential_id,
            "public_key": self.public_key,
            "sign_count": self.sign_count
        }
