from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from ..schemas.root import Health
from ..utils import get_version

router = APIRouter()

up_since = datetime.now(tz=datetime.now().astimezone().tzinfo)
version = get_version()

@router.get("/", include_in_schema=False)
def root():
    """Redirects the root URL to the API documentation.
    \f
    Returns:
        RedirectResponse: A response that redirects to the '/docs' URL.
    """
    return RedirectResponse(url='/docs')

@router.get("/health")
async def health_check() -> Health:
    """Health check endpoint.
    \f
    Returns:
        Health: A health check response.
    """
    return Health(
        status="healthy",
        version=version,
        up_since=str(up_since))
