from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.password import PasswordService

class UserService:
    """Service for handling user operations."""

    def __init__(self, session: AsyncSession):
        """Initialize the user service.

        Args:
            session: Async database session.
        """
        self.session = session
        self.password_service = PasswordService()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.

        Args:
            email: User's email address.

        Returns:
            Optional[User]: User if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User's UUID.

        Returns:
            Optional[User]: User if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data.

        Returns:
            User: Created user.

        Raises:
            HTTPException: If email already exists.
        """
        # Check if user exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Create user
        user_dict = user_data.model_dump()
        if user_data.password:
            user_dict["hashed_password"] = self.password_service.hash_password(
                user_data.password
            )
        user_dict.pop("password", None)

        user = User(**user_dict)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update_user(self, user_id: UUID, update_data: UserUpdate) -> User:
        """Update a user's information.

        Args:
            user_id: ID of user to update.
            update_data: Data to update.

        Returns:
            User: Updated user.

        Raises:
            HTTPException: If user not found or email already exists.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Check email uniqueness if being updated
        if update_data.email and update_data.email != user.email:
            existing_user = await self.get_user_by_email(update_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )

        # Update user fields
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_data.password:
            update_dict["hashed_password"] = self.password_service.hash_password(
                update_data.password
            )
        update_dict.pop("password", None)

        for key, value in update_dict.items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)

        return user
