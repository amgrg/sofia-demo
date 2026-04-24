"""Endpoint /chat."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import LIMITE_GIORNALIERO_LIBERO
from ..database import get_db
from ..deps import get_current_user
from ..model import genera_risposta_sync
from ..models import Messaggio, UsoGiornaliero, Utente
from ..schemas import ChatIn, ChatOut

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db), utente: Utente = Depends(get_current_user)):
    if not payload.messaggio.strip():
        raise HTTPException(status_code=400, detail="Messaggio vuoto")

    # Conta uso giornaliero
    oggi = date.today()
    uso = (
        db.query(UsoGiornaliero)
        .filter(UsoGiornaliero.utente_id == utente.id, UsoGiornaliero.giorno == oggi)
        .first()
    )
    if uso is None:
        uso = UsoGiornaliero(utente_id=utente.id, giorno=oggi, messaggi=0)
        db.add(uso)
        db.flush()

    limite = LIMITE_GIORNALIERO_LIBERO if utente.piano == "libero" else 10**9
    if utente.piano == "libero" and uso.messaggi >= limite:
        raise HTTPException(
            status_code=429,
            detail=f"Hai raggiunto il limite di {limite} messaggi al giorno del piano Libero. Passa a Professionale per messaggi illimitati.",
        )

    # Salva il messaggio dell'utente
    db.add(Messaggio(utente_id=utente.id, ruolo="user", contenuto=payload.messaggio))

    # Genera risposta tramite modello (o mock se SOFIA_USE_MOCK=1)
    risposta = genera_risposta_sync(payload.messaggio)
    db.add(Messaggio(utente_id=utente.id, ruolo="assistant", contenuto=risposta))

    uso.messaggi += 1
    db.commit()

    return ChatOut(
        risposta=risposta,
        messaggi_oggi=uso.messaggi,
        limite_giornaliero=limite,
    )
