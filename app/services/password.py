import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from ..models.user import User
from ..models.password import PasswordResetToken

class PasswordService:
    """Service for handling password-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the password service.

        Args:
            db: The database session.
        """
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password.
            hashed_password: Hashed password to compare against.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password.

        Args:
            password: Plain text password.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user with email and password.

        Args:
            email: The user's email.
            password: The password to verify.

        Returns:
            The authenticated user if successful, None otherwise.
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None

        return user

    async def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token for a user.

        Args:
            email: The email of the user requesting password reset.

        Returns:
            The reset token if successful, None if user not found.
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Generate token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Store token
        reset = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(reset)
        await self.db.commit()

        return token

    async def verify_reset_token(self, token: str) -> Optional[User]:
        """Verify a password reset token.

        Args:
            token: The token to verify.

        Returns:
            The user if token is valid, None otherwise.
        """
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        reset = result.scalar_one_or_none()

        if not reset:
            return None

        stmt = select(User).where(User.id == reset.user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def reset_password(
        self, token: str, new_password: str
    ) -> Optional[User]:
        """Reset a user's password using a reset token.

        Args:
            token: The reset token.
            new_password: The new password to set.

        Returns:
            The user if reset successful, None otherwise.
        """
        user = await self.verify_reset_token(token)
        if not user:
            return None

        # Update password
        user.hashed_password = self.get_password_hash(new_password)

        # Mark token as used
        stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
        result = await self.db.execute(stmt)
        reset = result.scalar_one()
        reset.is_used = True

        await self.db.commit()
        return user

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:
        """Change a user's password.

        Args:
            user: The user changing their password.
            current_password: The current password for verification.
            new_password: The new password to set.

        Returns:
            True if password change successful, False otherwise.
        """
        if not user.hashed_password:
            return False

        if not self.verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = self.get_password_hash(new_password)
        await self.db.commit()
        return True
