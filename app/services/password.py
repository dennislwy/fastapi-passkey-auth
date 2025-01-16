from passlib.context import CryptContext

class PasswordService:
    """Service for handling password-related operations."""

    def __init__(self):
        """Initialize the password service with bcrypt configuration."""
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password.
            hashed_password: Hashed password to compare against.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Hash a password.

        Args:
            password: Plain text password.

        Returns:
            str: Bcrypt hashed password.
        """
        return self.pwd_context.hash(password)