"""Configurazione centrale dell'app Sofia."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

# DB SQLite (file in data/)
DATABASE_URL = os.getenv(
    "SOFIA_DATABASE_URL",
    f"sqlite:///{DATA_DIR / 'sofia.db'}",
)

# JWT
SECRET_KEY = os.getenv("SOFIA_SECRET_KEY", "cambia-questa-chiave-in-produzione-sofia-demo")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("SOFIA_JWT_EXPIRE_MINUTES", "1440"))  # 24h

# Admin di default (creato dal seed)
DEFAULT_ADMIN_EMAIL = os.getenv("SOFIA_ADMIN_EMAIL", "admin@sofiaai.it")
DEFAULT_ADMIN_PASSWORD = os.getenv("SOFIA_ADMIN_PASSWORD", "admin1234")

# Limiti piano "libero"
LIMITE_GIORNALIERO_LIBERO = 30

# Server
HOST = os.getenv("SOFIA_HOST", "127.0.0.1")
PORT = int(os.getenv("SOFIA_PORT", "8000"))
