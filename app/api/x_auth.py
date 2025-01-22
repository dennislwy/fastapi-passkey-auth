from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from app.dependencies import get_db, CurrentUser
from app.config import settings
from app.models.base import AsyncSession
from app.schemas.login import LoginRequest
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token, RefreshToken
from app.models.auth import Authenticator
from app.schemas.webauthn import (
    WebAuthnRegisterOptions,
    WebAuthnAuthenticationOptions
)
from app.services.user import UserService
from app.services.auth import AuthService
from app.services.token import TokenService

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db)
) -> UserRead:
    """Register a new user with email and password.

    Args:
        user_data: User registration data.
        session: Database session.

    Returns:
        UserRead: Created user data.

    Raises:
        HTTPException: If email already exists.
    """
    user_service = UserService(session)

    # Check if user already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    user = await user_service.create_user(user_data)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db)
) -> Token:
    """Authenticate user with email and password.

    Args:
        response: FastAPI response object.
        credentials: Login credentials.
        session: Database session.

    Returns:
        Token: Access and refresh tokens.

    Raises:
        HTTPException: If authentication fails.
    """
    auth_service = AuthService(session)
    user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    token_service = TokenService(session)

    # Generate tokens
    tokens = Token(
        access_token=token_service.create_access_token(user.id),
        refresh_token=token_service.create_refresh_token(user.id)
    )

    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: RefreshToken,
    session: AsyncSession = Depends(get_db)
) -> Token:
    """Refresh access token using refresh token.

    Args:
        token: Refresh token.
        session: Database session.

    Returns:
        Token: New access and refresh tokens.

    Raises:
        HTTPException: If refresh token is invalid.
    """
    token_service = TokenService(session)
    token_data = token_service.verify_token(token.refresh_token, "refresh")

    if token_data:
        # Generate tokens
        tokens = Token(
            access_token=token_service.create_access_token(user.id),
            refresh_token=token_service.create_refresh_token(user.id)
        )

        return tokens

