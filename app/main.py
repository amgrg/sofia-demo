"""Entry point FastAPI per Sofia."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR
from .model import load_model
from .routers import admin as admin_router
from .routers import auth as auth_router
from .routers import chat as chat_router
from .routers import pages as pages_router
from .seed import seed_if_empty

app = FastAPI(
    title="Sofia AI — Demo locale",
    description="L'intelligenza artificiale italiana. Demo locale con backend FastAPI + SQLite.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS — permissivo per sviluppo locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(pages_router.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(chat_router.router)

# Mount statici (es. /static/landing.html)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup() -> None:
    seed_if_empty()
    load_model()


@app.get("/healthz", include_in_schema=False)
def health():
    return {"status": "ok", "app": "sofia-demo"}
