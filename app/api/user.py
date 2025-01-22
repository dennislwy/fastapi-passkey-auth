from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.dependencies import get_db, CurrentUser
from app.models.base import AsyncSession
from app.schemas.user import UserProfile, UserUpdate
from app.services.user import UserService

router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserProfile:
    """Get the current user information
    \f
    Args:
        current_user: Currently authenticated user.
        session: Database session.

    Returns:
        UserProfile: User profile with authenticator information.
    """
    user_service = UserService(session)
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return UserProfile.model_validate(user)


@router.patch("/me", response_model=UserProfile)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db)
) -> UserProfile:
    """Update the current user information.
    \f
    Args:
        update_data: Data to update.
        current_user: Currently authenticated user.
        session: Database session.

    Returns:
        UserProfile: Updated user profile.

    Raises:
        HTTPException: If email already exists or update fails.
    """
    user_service = UserService(session)
    updated_user = await user_service.update_user(current_user.id, update_data)
    return UserProfile.model_validate(updated_user)
