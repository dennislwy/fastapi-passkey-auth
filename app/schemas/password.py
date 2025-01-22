from pydantic import BaseModel, EmailStr

class PasswordForgotRequest(BaseModel):
    """Schema for password forgot request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""

    token: str
    new_password: str


class PasswordChange(BaseModel):
    """Schema for password change request."""

    current_password: str
    new_password: str