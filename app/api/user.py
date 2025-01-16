from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.base import AsyncSession
from ..models.user import User
from ..schemas.user import UserProfile

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get user profile and associated authenticators.
    \f
    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserProfile: User profile information including authenticators
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        authenticators=[auth.get_credential_data() for auth in current_user.authenticators]
    )
