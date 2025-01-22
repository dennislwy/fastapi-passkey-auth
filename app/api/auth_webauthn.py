import base64
import random
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import validator, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response
)
# from webauthn.helpers import (
#     options_to_json,
#     generate_challenge
# )
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    RegistrationCredential
)

from app.dependencies import get_db, CurrentUser
from app.services.user import UserService
from app.config import settings
from app.models.webauthn import WebAuthnCredential

router = APIRouter()
challenge_cache = {}

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
    def convert_response(cls, data: dict):
        """Convert response from a dictionary of strings to a dictionary of bytes"""
        assert isinstance(data, dict), 'response is not a dictionary'
        return {k: b64decode(v) for k, v in data.items()}

@router.post("/webauthn/register/generate-options")
async def generate_register_options(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PublicKeyCredentialCreationOptions:
    # Check if user exists
    user_service = UserService(db)
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_id = str(user.id)

    # Generate challenge
    challenge = generate_challenge()

    # Generate options
    options = generate_registration_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        rp_name=settings.WEBAUTHN_RP_NAME,
        user_name=user.email,
        user_id=user_id.encode('utf-8'),
        user_display_name=user.full_name,
        challenge=challenge
        )

    # Store challenge
    challenge_cache[user_id] = challenge

    return options

@router.post("/webauthn/register/verify")
async def verify_registration(
    current_user: CurrentUser,
    credential: CustomRegistrationCredential,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    user_id = str(current_user.id)
    expected_challenge = challenge_cache.get(user_id)

    if not expected_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    # Remove challenge from cache
    challenge_cache.pop(user_id)

    verification = verify_registration_response(
        credential=credential,
        expected_challenge=expected_challenge,
        expected_rp_id=settings.WEBAUTHN_RP_ID,
        expected_origin=settings.WEBAUTHN_ORIGIN
    )

    credential = WebAuthnCredential(
        credential_id=b64encode(verification.credential_id),
        credential_public_key=b64encode(verification.credential_public_key),
        sign_count=verification.sign_count,
        user_id=current_user.id
    )

    db.add(credential)
    await db.commit()

    return verification
