from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.dependencies import get_db, CurrentUser
from app.models.base import AsyncSession
from app.schemas.user import UserProfile, UserUpdate
from app.services.user import UserService

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: CurrentUser):
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
        full_name=current_user.full_name,
        email=current_user.email,
        is_active=current_user.is_active,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        authenticators=[auth.get_credential_data() for auth in current_user.authenticators]
    )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserProfile:
    """Get the current user's profile with associated authenticators.

    Args:
        current_user: Currently authenticated user.
        session: Database session.

    Returns:
        UserProfile: User profile with authenticator information.
    """
    # Refresh user data with authenticators
    user_service = UserService(session)
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return UserProfile.model_validate(user)


@router.patch("/me", response_model=UserProfile)
async def update_current_user(
    update_data: UserUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db)
) -> UserProfile:
    """Update the current user's profile information.

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

    # Check email uniqueness if being updated
    if update_data.email and update_data.email != current_user.email:
        existing_user = await user_service.get_user_by_email(update_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    updated_user = await user_service.update_user(current_user.id, update_data)
    return UserProfile.model_validate(updated_user)
