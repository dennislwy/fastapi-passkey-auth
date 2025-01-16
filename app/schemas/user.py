from pydantic import BaseModel, EmailStr
from typing import List

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str

class UserProfile(UserBase):
    """Schema for user profile response."""
    id: int
    is_active: bool
    authenticators: List[dict]

    class Config:
        from_attributes = True
