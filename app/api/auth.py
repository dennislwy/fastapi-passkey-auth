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

@router.post("/webauthn/register/generate-options", response_model=WebAuthnRegisterOptions)
async def webauthn_generate_register_options(
    current_user: CurrentUser
    ):
    """Generate WebAuthn registration options.
    \f
    Args:
        user: Current authenticated user
        db: Database session

    Returns:
        WebAuthnRegisterOptions: Registration options for the client
    """
    options = generate_registration_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        rp_name=settings.WEBAUTHN_RP_NAME,
        user_id=str(current_user.id),
        user_name=current_user.email,
        user_display_name=current_user.full_name
    )
    return WebAuthnRegisterOptions(public_key=options)

@router.post("/webauthn/register/verify")
async def webauthn_verify_register(
    credential: dict,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Verify WebAuthn registration response.
    \f
    Args:
        credential: Client credential response
        user: Current authenticated user
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If verification fails
    """
    try:
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=None,  # You should store and verify the challenge
            expected_origin=settings.WEBAUTHN_RP_ORIGIN,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
        )

        authenticator = Authenticator(
            user_id=current_user.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count
        )
        db.add(authenticator)
        db.commit()

        return {"message": "Registration successful"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

@router.get("/webauthn/authenticate/generate-options", response_model=WebAuthnAuthenticationOptions)
async def webauthn_generate_authentication_options():
    """Generate WebAuthn authentication options.
    \f
    Returns:
        WebAuthnAuthenticateOptions: Authentication options for the client
    """
    options = generate_authentication_options(
        rp_id=settings.WEBAUTHN_RP_ID,
    )
    return WebAuthnAuthenticationOptions(public_key=options)

@router.post("/webauthn/authenticate/verify")
async def webauthn_verify_authentication(
    credential: dict,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Verify WebAuthn authentication response.
    \f
    Args:
        credential: Client credential response
        db: Database session

    Returns:
        dict: JWT token upon successful authentication

    Raises:
        HTTPException: If verification fails
    """
    try:
        authenticator = db.query(Authenticator).filter(
            Authenticator.credential_id == credential["id"]
        ).first()

        if not authenticator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authenticator not found"
            )

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=None,  # You should store and verify the challenge
            expected_origin=settings.WEBAUTHN_RP_ORIGIN,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
            credential_public_key=authenticator.public_key,
            credential_current_sign_count=authenticator.sign_count,
        )

        # Update sign count & last used time
        authenticator.sign_count = verification.new_sign_count
        authenticator.last_used_at = datetime.now(timezone.utc)
        db.commit()

        # Generate JWT token
        token = jwt.encode(
            {"sub": str(authenticator.user_id)},
            settings.SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM
        )

        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
