from fastapi import APIRouter

from app.api import root, user, auth_login, auth_webauthn, static

router = APIRouter()

router.include_router(root.router, prefix="", tags=["root"])
router.include_router(static.router, prefix="", tags=["static"])

# router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(auth_login.router, prefix="/auth", tags=["auth"])
router.include_router(auth_webauthn.router, prefix="/auth", tags=["auth/webauthn"])
router.include_router(user.router, prefix="/user", tags=["user"])
