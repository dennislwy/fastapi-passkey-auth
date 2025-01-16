from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from jose import jwt
from jose.exceptions import JWTError
from ..schemas.token import TokenData
from ..config import settings

class TokenService:
    """Service for handling JWT token operations."""

    def create_access_token(self, user_id: UUID) -> str:
        """Create a JWT access token.

        Args:
            user_id: User's UUID.

        Returns:
            str: JWT access token.
        """
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access"
        }

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a JWT refresh token.

        Args:
            user_id: User's UUID.

        Returns:
            str: JWT refresh token.
        """
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def verify_token(self, token: str, token_type: str) -> Optional[TokenData]:
        """Verify a JWT token.

        Args:
            token: JWT token to verify.
            token_type: Type of token ("access" or "refresh").

        Returns:
            Optional[TokenData]: Token data if valid, None otherwise.

        Raises:
            HTTPException: If token is invalid or expired.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )

            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload"
                )

            return TokenData(user_id=UUID(user_id))

        except JWTError as exc:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            ) from exc
