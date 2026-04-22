"""Dependency FastAPI: utente corrente, admin only, ecc."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .auth import decode_token
from .database import get_db
from .models import Utente

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Utente:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante")
    payload = decode_token(creds.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")
    utente = db.query(Utente).filter(Utente.email == payload["sub"]).first()
    if not utente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utente non trovato")
    if not utente.attivo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabilitato")
    return utente


def require_admin(utente: Utente = Depends(get_current_user)) -> Utente:
    if utente.ruolo != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso riservato agli amministratori")
    return utente
