from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# AsyncSessionLocal = sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()
