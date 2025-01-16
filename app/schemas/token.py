from uuid import UUID
from pydantic import BaseModel

class TokenData(BaseModel):
    """Schema for JWT token data."""
    user_id: UUID

class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshToken(BaseModel):
    """Schema for token refresh requests."""
    refresh_token: str
