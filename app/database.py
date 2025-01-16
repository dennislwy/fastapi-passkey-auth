from alembic import command, config
from .models.base import Base, engine

# Create database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")

# https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio
async def run_async_upgrade():
    # async_engine = create_async_engine("sqlite+aiosqlite://", echo=True)
    # async with async_engine.begin() as conn:
    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, config.Config("alembic.ini"))
