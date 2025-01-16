import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .database import init_db, run_async_upgrade
from .api import auth, user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the lifespan of the FastAPI application.

    This context manager handles the startup and shutdown events of the FastAPI app.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None

    Raises:
        Exception: If there is an error during startup or shutdown.
    """
    try:
        await startup()
        yield
    finally:
        await shutdown()

app = FastAPI(
    title="FastAPI Passkey Auth Demo",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])

@app.get("/", include_in_schema=False)
def root():
    """Redirects the root URL to the API documentation.
    \f
    Returns:
        RedirectResponse: A response that redirects to the '/docs' URL.
    """
    return RedirectResponse(url='/docs')

async def startup():
    """Handles the startup event of the FastAPI application.

    This function initializes the database and runs Alembic migrations.

    Raises:
        Exception: If there is an error during database initialization or migration.
    """
    logging.info("Starting up server")

    # Create database tables
    await init_db()

    # Run Alembic migrations
    await run_async_upgrade()

async def shutdown():
    """Handles the shutdown event of the FastAPI application.

    This function logs the shutdown event.

    Raises:
        Exception: If there is an error during shutdown.
    """
    logging.info("Shutting down server")
