"""Pydantic schemas for user-related operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict

from app.schemas.webauthn import AuthenticatorRead

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for updating user data."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserRead(UserBase):
    """Schema for reading user data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

class UserProfile(UserRead):
    """Schema for user profile including authenticators."""
    authenticators: List[AuthenticatorRead]
