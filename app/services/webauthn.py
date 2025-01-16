from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
)
from webauthn.helpers import bytes_to_base64url
from ..models.user import User
from ..models.auth import Authenticator, AuthenticatorCreate
from ..schemas.webauthn import WebAuthnRegisterOptions
from ..config import settings

class WebAuthnService:
    """Service for handling WebAuthn/passkey operations."""

    def __init__(self, session: AsyncSession):
        """Initialize the WebAuthn service.

        Args:
            session: Async database session.
        """
        self.session = session

    async def generate_registration_opts(self, user: User) -> WebAuthnRegisterOptions:
        """Generate WebAuthn registration options for a user.

        Args:
            user: User to generate options for.

        Returns:
            WebAuthnRegisterOptions: Registration options for WebAuthn.
        """
        options = generate_registration_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            rp_name=settings.WEBAUTHN_RP_NAME,
            user_id=str(user.id),
            user_name=user.email,
            user_display_name=user.full_name,
        )

        return WebAuthnRegisterOptions(**options_to_json(options))

    async def verify_registration(
        self,
        user: User,
        credential: dict
    ) -> Authenticator:
        """Verify WebAuthn registration response and create authenticator.

        Args:
            user: User registering the authenticator.
            credential: WebAuthn credential response.

        Returns:
            Authenticator: Created authenticator record.

        Raises:
            HTTPException: If verification fails.
        """
        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=self.current_challenge,  # You'll need to implement challenge storage
                expected_origin=settings.WEBAUTHN_RP_ORIGIN,
                expected_rp_id=settings.WEBAUTHN_RP_ID
            )

            # Create authenticator record
            authenticator_data = AuthenticatorCreate(
                credential_id=verification.credential_id,
                public_key=verification.credential_public_key,
                sign_count=verification.sign_count,
                # device_type=credential.get("type", "unknown"),
                # backup_eligible=verification.backup_eligible,
                # backup_state=verification.backup_state
            )

            authenticator = Authenticator(
                user_id=user.id,
                **authenticator_data.model_dump()
            )

            self.session.add(authenticator)
            await self.session.commit()
            await self.session.refresh(authenticator)

            return authenticator

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Registration verification failed: {str(e)}"
            ) from e

    async def generate_authentication_options(self, user: User) -> dict:
        """Generate WebAuthn authentication options for a user.

        Args:
            user: User to authenticate.

        Returns:
            dict: Authentication options for WebAuthn.
        """
        # Get user's authenticators
        result = await self.session.execute(
            select(Authenticator).where(Authenticator.user_id == user.id)
        )
        authenticators = result.scalars().all()

        if not authenticators:
            raise HTTPException(
                status_code=400,
                detail="No authenticators registered for user"
            )

        options = generate_authentication_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            allow_credentials=[{
                "type": "public-key",
                "id": bytes_to_base64url(auth.credential_id)
            } for auth in authenticators]
        )

        return options_to_json(options)

    async def verify_authentication(self, credential: dict) -> User:
        """Verify WebAuthn authentication response.

        Args:
            credential: WebAuthn credential response.

        Returns:
            User: Authenticated user.

        Raises:
            HTTPException: If verification fails.
        """
        try:
            credential_id = base64url_to_bytes(credential["id"])

            # Get authenticator
            result = await self.session.execute(
                select(Authenticator).where(
                    Authenticator.credential_id == credential_id
                )
            )
            authenticator = result.scalar_one_or_none()

            if not authenticator:
                raise HTTPException(
                    status_code=400,
                    detail="Authenticator not found"
                )

            # Verify the authentication response
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=self.current_challenge,  # You'll need to implement challenge storage
                expected_origin=settings.WEBAUTHN_RP_ORIGIN,
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                credential_public_key=authenticator.public_key,
                credential_current_sign_count=authenticator.sign_count
            )

            # Update sign count
            authenticator.sign_count = verification.new_sign_count
            authenticator.last_used_at = datetime.now(timezone.utc)
            await self.session.commit()

            # Get and return user
            result = await self.session.execute(
                select(User).where(User.id == authenticator.user_id)
            )
            return result.scalar_one()

        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed: {str(e)}"
            ) from e