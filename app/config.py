from typing import Any, Dict
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings.

    Args:
        DEBUG: Enable debug mode
        DATABASE_URL: SQLAlchemy database URL
        SECRET_KEY: Secret key for JWT encoding
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days
        RP_ID: Relying Party ID for WebAuthn
        RP_NAME: Relying Party name for WebAuthn
        RP_ORIGIN: Application origin URL
    """
    # Application Settings
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str

    # Security Settings
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # WebAuthn Settings
    RP_ID: str
    RP_NAME: str
    RP_ORIGIN: str

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
        if not v.startswith(("sqlite+aiosqlite:", "postgresql+asyncpg:")):
            raise ValueError("Database URL must be for an async database")
        return v

    @property
    def webauthn_config(self) -> Dict[str, Any]:
        """Get WebAuthn configuration as a dictionary.

        Returns:
            A dictionary containing WebAuthn configuration parameters.
        """
        return {
            "rp_id": self.RP_ID,
            "rp_name": self.RP_NAME,
            "rp_origin": self.RP_ORIGIN,
        }

    class Config:
        env_file = ".env"

# Create a global settings instance
settings = Settings()
