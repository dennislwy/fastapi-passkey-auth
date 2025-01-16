from typing import Any, Dict
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings.

    Args:
        DEBUG: Enable debug mode
        DATABASE_URL: SQLAlchemy database URL
        SECRET_KEY: Secret key for JWT encoding
        JWT_ALGORITHM: JWT algorithm
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days
        WEBAUTHN_RP_ID: Relying Party ID for WebAuthn
        WEBAUTHN_RP_NAME: Relying Party name for WebAuthn
        WEBAUTHN_RP_ORIGIN: Application origin URL
    """
    # Application Settings
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str

    # Security Settings
    SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # WebAuthn Settings
    WEBAUTHN_RP_ID: str
    WEBAUTHN_RP_NAME: str
    WEBAUTHN_RP_ORIGIN: str

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate the database URL format.

        Args:
            v: The database URL string to validate.

        Returns:
            The validated database URL.

        Raises:
            ValueError: If the database URL format is invalid.
        """
        if v.startswith("sqlite+aiosqlite:"):
            return v
        elif v.startswith("sqlite:"):
            # Ensure async driver is used
            return v.replace("sqlite:", "sqlite+aiosqlite:", 1)
        raise ValueError("Only SQLite databases are supported")

    @property
    def webauthn_config(self) -> Dict[str, Any]:
        """Get WebAuthn configuration as a dictionary.

        Returns:
            A dictionary containing WebAuthn configuration parameters.
        """
        return {
            "rp_id": self.WEBAUTHN_RP_ID,
            "rp_name": self.WEBAUTHN_RP_NAME,
            "rp_origin": self.WEBAUTHN_RP_ORIGIN,
        }

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings instance
settings = Settings()
