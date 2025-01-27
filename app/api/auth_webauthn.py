import base64
import random
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import validator, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    base64url_to_bytes
)
# from webauthn.helpers import (
#     options_to_json,
#     generate_challenge
# )
from webauthn.registration.verify_registration_response import VerifiedRegistration
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    RegistrationCredential,
    PublicKeyCredentialRequestOptions
)

from app.dependencies import get_db, CurrentUser
from app.config import settings
from app.models.webauthn import WebAuthnCredential
from app.models.user import User
from app.utils.webauthn import (
    get_user_webauthn_credentials,
    generate_authentication_options_for_user
)
from app.schemas.token import Token
from app.services.token import TokenService

WEBAUTHN_REGISTER_CHALLENGE = "webauthn_register_challenge"

router = APIRouter()
challenge_cache = {} # Memory cache to store challenges

def generate_challenge(n: int = 64) -> bytes:
    # Generate n random bytes in the ASCII printable range
    return bytes(random.choices(range(0x20, 0x7F), k=n))

def b64decode(s: str) -> bytes:
    """Decode a base64url-encoded string to bytes"""
    return base64.urlsafe_b64decode(s.encode())

def b64encode(b: bytes) -> str:
    """Encode bytes to a base64url-encoded string"""
    return base64.urlsafe_b64encode(b).decode()

class CustomRegistrationCredential(RegistrationCredential):
    @validator('raw_id', pre=True)
    def convert_raw_id(cls, v: str) -> bytes:
        """Convert raw_id from a string to bytes"""
        assert isinstance(v, str), 'raw_id is not a string'
        return b64decode(v)

    @validator('response', pre=True)
    def convert_response(cls, data: dict) -> dict:
        """Convert response from a dictionary of strings to a dictionary of bytes"""
        assert isinstance(data, dict), 'response is not a dictionary'
        return {k: b64decode(v) for k, v in data.items()}

@router.post("/webauthn/register/generate-options")
async def generate_register_options(
    request: Request,
    current_user: CurrentUser
) -> PublicKeyCredentialCreationOptions:
    user_id = str(current_user.id)

    # Generate challenge
    challenge = generate_challenge()

    # Generate options
    options = generate_registration_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        rp_name=settings.WEBAUTHN_RP_NAME,
        user_name=current_user.email,
        user_id=user_id.encode('utf-8'),
        user_display_name=current_user.full_name,
        challenge=challenge
        )

    # Store challenge in session for verification
    # challenge_cache[user_id] = challenge
    request.session[WEBAUTHN_REGISTER_CHALLENGE] = base64.b64encode(options.challenge).decode()

    return options

@router.post("/webauthn/register/verify")
async def verify_registration(
    request: Request,
    credential: CustomRegistrationCredential,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> VerifiedRegistration:
    try:
        # Get expected challenge
        user_id = str(current_user.id)

        # Get expected challenge from session
        # expected_challenge = challenge_cache.get(user_id)
        expected_challenge = base64.b64decode(request.session[WEBAUTHN_REGISTER_CHALLENGE].encode())

        if not expected_challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found",
            )

        # Verify registration
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
            expected_origin=settings.WEBAUTHN_RP_ORIGIN
        )

        # Store webauthn credential in database
        credential = WebAuthnCredential(
            credential_id=b64encode(verification.credential_id),
            credential_public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            credential_device_type=verification.credential_device_type,
            credential_backed_up=verification.credential_backed_up,
            user_id=current_user.id
        )
        db.add(credential)
        await db.commit()

        return verification

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)) from e

    finally:
        # Clear challenge from session data
        # challenge_cache.pop(user_id)
        request.session.pop(WEBAUTHN_REGISTER_CHALLENGE, None)

# @router.get("/webauthn/authenticate/generate-options")
# async def generate_authenticate_options(
#     request: Request,
#     email: str,
#     session: Annotated[AsyncSession, Depends(get_db)]
# ) -> PublicKeyCredentialRequestOptions:
#     """Generate authentication options for a user's WebAuthn credentials."""
#     try:
#         # Find the user by email
#         result = await session.execute(
#             select(User).where(User.email == email)
#         )
#         user = result.scalar_one_or_none()
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found",
#             )

#         # Get user's webauthn credentials
#         result = await session.execute(
#             select(WebAuthnCredential).where(WebAuthnCredential.user_id == user.id)
#         )
#         credentials = get_user_webauthn_credentials(session, user.id)

#         if not credentials:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No registered webauthn credentials found for this user",
#             )

#         # Generate authentication options
#         options = generate_authentication_options_for_user(credentials)

#         # Store challenge in session for verification
#         request.session["authentication_challenge"] = options.challenge
#         request.session["user_id"] = str(user.id)

#         return options

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)) from e

# @router.post("/webauthn/authenticate/verify")
# async def verify_authentication(
#     request: Request,
#     authentication_response: dict,
#     session: AsyncSession = Depends(get_db),
# ) -> Token:
#     """Verify WebAuthn authentication response and issue JWT tokens."""
#     # Get stored challenge and user_id from session
#     challenge = request.session.get("authentication_challenge")
#     user_id = request.session.get("user_id")

#     if not challenge or not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid session state",
#         )

#     # Get user and credential
#     credential_id = authentication_response["id"]
#     result = await session.execute(
#         select(WebAuthnCredential).where(
#             WebAuthnCredential.credential_id == credential_id,
#             WebAuthnCredential.user_id == user_id,
#         )
#     )
#     credential = result.scalar_one_or_none()

#     if not credential:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Credential not found",
#         )

#     try:
#         verification = verify_authentication_response(
#             credential=authentication_response,
#             expected_challenge=base64url_to_bytes(challenge),
#             expected_origin=settings.WEBAUTHN_RP_ORIGIN,
#             expected_rp_id=settings.WEBAUTHN_RP_ID,
#             credential_public_key=base64url_to_bytes(credential.credential_public_key),
#             credential_current_sign_count=credential.sign_count,
#             require_user_verification=True
#         )

#         # Update credential sign count
#         credential.sign_count = verification.new_sign_count
#         await session.commit()

#         # Clear session data
#         request.session.pop("authentication_challenge", None)
#         request.session.pop("user_id", None)

#         # Generate tokens
#         token_service = TokenService()
#         access_token, refresh_token = token_service.create_tokens(user_id, )

#         return Token(
#             access_token=access_token,
#             refresh_token=refresh_token
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)) from e

