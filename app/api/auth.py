from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
from jose import jwt
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from ..dependencies import get_db, get_current_user
from ..models.base import AsyncSession
from ..models.user import User, Authenticator
from ..schemas.auth import WebAuthnRegisterOptions, WebAuthnAuthenticateOptions
from ..config import settings

router = APIRouter()

@router.post("/webauthn/register/generate-options", response_model=WebAuthnRegisterOptions)
async def webauthn_generate_register_options(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
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
        rp_id=settings.RP_ID,
        rp_name=settings.RP_NAME,
        user_id=str(user.id),
        user_name=user.email,
    )
    return WebAuthnRegisterOptions(public_key=options)

@router.post("/webauthn/register/verify")
async def webauthn_verify_register(
    credential: dict,
    user: Annotated[User, Depends(get_current_user)],
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
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
        )

        authenticator = Authenticator(
            user_id=user.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
        )
        db.add(authenticator)
        db.commit()

        return {"message": "Registration successful"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

@router.get("/webauthn/authenticate/generate-options", response_model=WebAuthnAuthenticateOptions)
async def webauthn_generate_authentication_options():
    """Generate WebAuthn authentication options.
    \f
    Returns:
        WebAuthnAuthenticateOptions: Authentication options for the client
    """
    options = generate_authentication_options(
        rp_id=settings.RP_ID,
    )
    return WebAuthnAuthenticateOptions(public_key=options)

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
            expected_origin=settings.RP_ORIGIN,
            expected_rp_id=settings.RP_ID,
            credential_public_key=authenticator.public_key,
            credential_current_sign_count=authenticator.sign_count,
        )

        # Update sign count
        authenticator.sign_count = verification.new_sign_count
        db.commit()

        # Generate JWT token
        token = jwt.encode(
            {"sub": str(authenticator.user_id)},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
