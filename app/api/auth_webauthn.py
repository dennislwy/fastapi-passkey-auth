import base64
import random
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn import (
    generate_registration_options,
)
# from webauthn.helpers import (
#     options_to_json,
#     generate_challenge
# )
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions
)
from app.dependencies import get_db, CurrentUser
from app.services.user import UserService
from app.config import settings

router = APIRouter()

def generate_challenge(n: int = 64) -> bytes:
    # Generate n random bytes in the ASCII printable range
    return bytes(random.choices(range(0x20, 0x7F), k=n))

@router.post("/webauthn/register/generate-options")
async def generate_registration_opts(
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
    challenge_base64 = base64.b64encode(challenge).decode('utf-8')

    # Generate options
    options = generate_registration_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        rp_name=settings.WEBAUTHN_RP_NAME,
        user_name=user.email,
        user_id=user_id.encode('utf-8'),
        user_display_name=user.full_name,
        challenge=challenge
        )

    return options
