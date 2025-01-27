from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    with open("static/index.html") as fh:
        return fh.read()

class CSSResponse(HTMLResponse):
    media_type = "text/css"

class JavascriptResponse(HTMLResponse):
    media_type = "application/javascript"

@router.get("/webauthn_client.js", response_class=JavascriptResponse, include_in_schema=False)
async def client_js():
    return Path("static/webauthn_client.js").read_bytes()

@router.get("/styles.css", response_class=CSSResponse, include_in_schema=False)
async def client_css():
    return Path("static/styles.css").read_bytes()
