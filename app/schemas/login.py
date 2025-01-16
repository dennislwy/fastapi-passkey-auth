from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """Schema for traditional login requests."""
    email: EmailStr
    password: str
