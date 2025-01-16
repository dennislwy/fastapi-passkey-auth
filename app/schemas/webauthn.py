from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class AuthenticatorCreate(BaseModel):
    """Schema for creating a new WebAuthn authenticator."""
    credential_id: bytes
    public_key: bytes
    sign_count: int
    device_type: str
    backup_eligible: bool
    backup_state: bool


class AuthenticatorRead(BaseModel):
    """Schema for reading WebAuthn authenticator data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    credential_id: bytes
    device_type: str
    backup_eligible: bool
    backup_state: bool
    created_at: datetime
    last_used_at: Optional[datetime]


class WebAuthnRegisterOptions(BaseModel):
    """Schema for WebAuthn registration options."""
    rp_id: str
    rp_name: str
    user_id: str
    user_name: str
    challenge: bytes
    pubkey_cred_params: List[dict]
    timeout: int
    authenticator_selection: dict
    attestation: str


class WebAuthnAuthenticationOptions(BaseModel):
    """Schema for WebAuthn authentication options."""
    challenge: bytes
    timeout: int
    rp_id: str
    allow_credentials: List[dict]
    user_verification: str
