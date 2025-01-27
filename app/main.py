import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, run_async_upgrade
from app.utils.version import get_version
from app.routers import router
from app.config import settings

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler.

    Args:
        exc_type (Type[BaseException]): The exception type.
        exc_value (BaseException): The exception instance.
        exc_traceback (TracebackType): The traceback object.

    This function logs uncaught exceptions and suppresses the stack trace for keyboard
    interrupts to allow graceful shutdowns.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

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

# Create FastAPI application
app = FastAPI(
    title="FastAPI Passkey Auth Demo",
    version=get_version(),
    contact={"name": "Dennis Lee"},
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add Session Middleware (must be added before CORS)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="webauthn",
    max_age=120,  # 1 hour in seconds
    same_site="strict",
    https_only=settings.HTTPS_ONLY
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

async def startup():
    """Handles the startup event of the FastAPI application.

    This function initializes the database and runs Alembic migrations.

    Raises:
        Exception: If there is an error during database initialization or migration.
    """
    logging.info("Starting up server")

    # Run Alembic migrations
    # await run_async_upgrade()

    # Create database tables
    await init_db()

async def shutdown():
    """Handles the shutdown event of the FastAPI application.

    This function logs the shutdown event.

    Raises:
        Exception: If there is an error during shutdown.
    """
    logging.info("Shutting down server")

if __name__ == "__main__":
    import uvicorn
    # Start the server
    uvicorn.run("main:app", host="0.0.0.0")
