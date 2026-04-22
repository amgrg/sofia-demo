"""Setup SQLAlchemy / sessione DB."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL, DATA_DIR

# Assicura che la cartella data/ esista
DATA_DIR.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    """Dependency FastAPI: apre/chiude una sessione DB per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
