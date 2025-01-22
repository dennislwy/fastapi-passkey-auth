from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, GUID

# class WebAuthnCredential(Base):
#     __tablename__ = "webauthn_credentials"

#     credential_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
#     credential_public_key: Mapped[str] = mapped_column(String(255), nullable=False)
#     sign_count: Mapped[int] = mapped_column(nullable=False, default=0)
#     transports: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

#     # Foreign keys
#     user_id: Mapped[GUID] = mapped_column(ForeignKey("users.id"))

#     # Relationships
#     user: Mapped["User"] = relationship(back_populates="webauthn_credentials")
