from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .password import PasswordService
from .token import TokenService
from .user import UserService
from .webauthn import WebAuthnService
from ..models.user import User
from ..models.token import Token

class AuthService:
    """Main authentication service that orchestrates other services."""

    def __init__(self, session: AsyncSession):
        """Initialize the authentication service.

        Args:
            session: Async database session.
        """
        self.session = session
        self.user_service = UserService(session)
        self.password_service = PasswordService()
        self.token_service = TokenService()
        self.webauthn_service = WebAuthnService(session)

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user with email and password.

        Args:
            email: User's email.
            password: User's password.

        Returns:
            Optional[User]: Authenticated user or None if authentication fails.
        """
        user = await self.user_service.get_user_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not self.password_service.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_tokens(self, user_id: UUID) -> Token:
        """Create access and refresh tokens for a user.

        Args:
            user_id: User's UUID.

        Returns:
            Token: Access and refresh tokens.
        """
        access_token = self.token_service.create_access_token(user_id)
        refresh_token = self.token_service.create_refresh_token(user_id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_tokens(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token.

        Returns:
            Token: New access and refresh tokens.

        Raises:
            HTTPException: If refresh token is invalid.
        """
        token_data = self.token_service.verify_token(refresh_token, "refresh")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return self.create_tokens(token_data.user_id)
