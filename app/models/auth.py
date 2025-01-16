from typing import Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUID

class Authenticator(Base):
    """WebAuthn authenticator model.

    Attributes:
        credential_id: Base64 encoded credential ID
        public_key: Base64 encoded public key
        sign_count: Number of times the authenticator has been used
        user_id: ID of the associated user
        user: Reference to the associated user
        last_used_at: Timestamp of the last time the authenticator was used
    """
    __tablename__ = "authenticators"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, index=True)
    credential_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    public_key: Mapped[str] = mapped_column(String(255))

    # credential_id: Mapped[bytes] = mapped_column(LargeBinary, unique=True, index=True)
    # public_key: Mapped[bytes] = mapped_column(LargeBinary)
    # device_type: Mapped[str] = mapped_column(String(32))
    # backup_eligible: Mapped[bool] = mapped_column(default=False)
    # backup_state: Mapped[bool] = mapped_column(default=False)

    sign_count: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="authenticators")

    def get_credential_data(self):
        """Convert stored credential data to dictionary format."""
        return {
            "credential_id": self.credential_id,
            "public_key": self.public_key,
            "sign_count": self.sign_count
        }
