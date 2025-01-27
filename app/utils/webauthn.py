from webauthn import (
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    AuthenticatorTransport,
    PublicKeyCredentialType,
    PublicKeyCredentialRequestOptions
)
from typing import List
from sqlalchemy import select
from ..models.webauthn import WebAuthnCredential
from ..config import settings

async def get_user_webauthn_credentials(session, user_id: str) -> List[WebAuthnCredential]:
    """Retrieve all WebAuthn credentials for a user."""
    result = await session.execute(
        select(WebAuthnCredential).where(WebAuthnCredential.user_id == user_id)
    )
    return result.scalars().all()

def parse_transports(transports_str: str | None) -> List[AuthenticatorTransport] | None:
    """Parse transport string into AuthenticatorTransport enum values."""
    if not transports_str:
        return None
    return [AuthenticatorTransport(t) for t in transports_str.split(",")]

def generate_authentication_options_for_user(
    credentials: List[WebAuthnCredential]
    ) -> PublicKeyCredentialRequestOptions:
    """Generate authentication options for a user's credentials."""
    allow_credentials = [
        PublicKeyCredentialDescriptor(
            type=PublicKeyCredentialType.PUBLIC_KEY,
            id=base64url_to_bytes(cred.credential_id),
            transports=parse_transports(cred.transports)
        )
        for cred in credentials
    ]

    options = generate_authentication_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        allow_credentials=allow_credentials,
        user_verification="preferred"
    )
    return options
