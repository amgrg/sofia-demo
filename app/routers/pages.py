"""Serve le pagine HTML statiche con URL puliti: /, /demo, /admin."""
from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from ..config import STATIC_DIR

router = APIRouter(tags=["pages"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def landing():
    return FileResponse(STATIC_DIR / "landing.html")


@router.get("/demo", response_class=HTMLResponse)
def demo():
    return FileResponse(STATIC_DIR / "demo.html")


@router.get("/admin", response_class=HTMLResponse)
def admin_page():
    return FileResponse(STATIC_DIR / "admin.html")
