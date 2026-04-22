"""Endpoint /auth/* — login e registrazione."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, hash_password, verify_password
from ..database import get_db
from ..models import Utente
from ..schemas import LoginIn, RegisterIn, TokenOut, UtenteOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    utente = db.query(Utente).filter(Utente.email == payload.email).first()
    if not utente or not verify_password(payload.password, utente.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o password errate")
    if not utente.attivo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabilitato")

    utente.ultimo_accesso = datetime.utcnow()
    db.commit()
    db.refresh(utente)

    token = create_access_token(utente.email, extra={"ruolo": utente.ruolo})
    return TokenOut(access_token=token, utente=UtenteOut.model_validate(utente))


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(Utente).filter(Utente.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email già registrata")

    utente = Utente(
        email=payload.email,
        password_hash=hash_password(payload.password),
        nome=payload.nome,
        cognome=payload.cognome,
        ruolo="utente",
        piano="libero",
        attivo=True,
    )
    db.add(utente)
    db.commit()
    db.refresh(utente)

    token = create_access_token(utente.email, extra={"ruolo": utente.ruolo})
    return TokenOut(access_token=token, utente=UtenteOut.model_validate(utente))
