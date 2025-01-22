"""Authentication routes for login, logout, and token refresh."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse
from app.schemas.token import Token
from app.services.password import PasswordService
from app.services.token import TokenService

router = APIRouter()

@router.post("/register")
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserCreateResponse:
    """Create a new user account.
    \f
    Args:
        user_data: The user data for creating the account.
        db: The database session.

    Returns:
        The created user.

    Raises:
        HTTPException: If email already exists.
    """
    # Check if email exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    password_service = PasswordService(db)
    hashed_password = password_service.get_password_hash(user_data.password)

    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )

    # Add user to database
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserCreateResponse(id=user.id)

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """Login with email and password.
    \f
    Args:
        form_data: The login credentials.
        db: The database session.

    Returns:
        Access and refresh tokens.

    Raises:
        HTTPException: If authentication fails.
    """
    password_service = PasswordService(db)
    user = await password_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token_service = TokenService()
    access_token, refresh_token = token_service.create_tokens(user.id, user.email)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )
