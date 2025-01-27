from typing import Optional
from sqlalchemy import String, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, GUID

class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    credential_id: Mapped[str] = mapped_column(String, primary_key=True, index=True, nullable=False)
    credential_public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    sign_count: Mapped[int] = mapped_column(nullable=False, default=0)
    credential_backed_up: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    credential_device_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Foreign keys
    user_id: Mapped[GUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="credentials")
