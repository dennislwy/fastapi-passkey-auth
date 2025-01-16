from datetime import datetime, timezone
from sqlalchemy.types import BINARY, TypeDecorator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )

# SQLite doesn't support UUID natively, so we need to use a custom type decorator
# https://stackoverflow.com/questions/5849389/storing-uuids-in-sqlite-using-pylons-and-sqlalchemy
# https://gist.github.com/gmolveau/7caeeefe637679005a7bb9ae1b5e421e
class UUID(TypeDecorator):
    impl = BINARY