from pydantic import BaseModel
from typing import Dict, Any, Optional

class WebAuthnRegisterOptions(BaseModel):
    """Schema for WebAuthn registration options."""
    public_key: Dict[str, Any]

class WebAuthnAuthenticateOptions(BaseModel):
    """Schema for WebAuthn authentication options."""
    public_key: Dict[str, Any]