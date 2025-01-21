"""Authentication routes for login, logout, and token refresh."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse
from app.services.password import PasswordService

router = APIRouter()

@router.post("/signup", response_model=UserCreateResponse)
async def signup(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a new user account.

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
        password_hash=hashed_password,
        full_name=user_data.full_name,
    )

    # Add user to database
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserCreateResponse(id=user.id)
