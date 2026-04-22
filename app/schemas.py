"""Pydantic schemas per request/response."""
from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, EmailStr, Field


# ---- AUTH ----

class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)
    nome: str = ""
    cognome: str = ""


class UtenteOut(BaseModel):
    email: EmailStr
    nome: str
    cognome: Optional[str] = ""
    ruolo: str
    piano: str
    attivo: bool

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utente: UtenteOut


# ---- ADMIN ----

class StatsOut(BaseModel):
    totale_utenti: int
    utenti_attivi_oggi: int
    messaggi_oggi: int
    totale_messaggi: int
    per_piano: Dict[str, int]


class UtenteAdminOut(BaseModel):
    email: EmailStr
    nome: str
    cognome: Optional[str] = ""
    piano: str
    attivo: bool
    messaggi_oggi: int
    limite_giornaliero: int
    totale_messaggi: int
    creato_il: datetime


class UtentiListOut(BaseModel):
    utenti: List[UtenteAdminOut]


class CambiaPianoIn(BaseModel):
    email: EmailStr
    piano: str  # 'libero' | 'professionale' | 'aziende'


# ---- CHAT ----

class ChatIn(BaseModel):
    messaggio: str


class ChatOut(BaseModel):
    risposta: str
    messaggi_oggi: int
    limite_giornaliero: int
