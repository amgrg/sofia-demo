"""Endpoint /admin/* — solo per ruolo admin."""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import LIMITE_GIORNALIERO_LIBERO
from ..database import get_db
from ..deps import require_admin
from ..models import Messaggio, UsoGiornaliero, Utente
from ..schemas import CambiaPianoIn, StatsOut, UtenteAdminOut, UtentiListOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

PIANI_VALIDI = {"libero", "professionale", "aziende"}


def _messaggi_oggi(db: Session, utente_id: int) -> int:
    row = (
        db.query(UsoGiornaliero)
        .filter(UsoGiornaliero.utente_id == utente_id, UsoGiornaliero.giorno == date.today())
        .first()
    )
    return row.messaggi if row else 0


def _limite_per_piano(piano: str) -> int:
    if piano == "libero":
        return LIMITE_GIORNALIERO_LIBERO
    return 10**9  # praticamente illimitato


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    totale_utenti = db.query(func.count(Utente.id)).scalar() or 0

    oggi = date.today()
    inizio_oggi = datetime.combine(oggi, datetime.min.time())

    utenti_attivi_oggi = (
        db.query(func.count(func.distinct(UsoGiornaliero.utente_id)))
        .filter(UsoGiornaliero.giorno == oggi, UsoGiornaliero.messaggi > 0)
        .scalar()
        or 0
    )

    messaggi_oggi = (
        db.query(func.coalesce(func.sum(UsoGiornaliero.messaggi), 0))
        .filter(UsoGiornaliero.giorno == oggi)
        .scalar()
        or 0
    )

    totale_messaggi = db.query(func.count(Messaggio.id)).scalar() or 0

    per_piano_rows = (
        db.query(Utente.piano, func.count(Utente.id))
        .group_by(Utente.piano)
        .all()
    )
    per_piano = {p: 0 for p in PIANI_VALIDI}
    for piano, n in per_piano_rows:
        if piano in per_piano:
            per_piano[piano] = n

    return StatsOut(
        totale_utenti=totale_utenti,
        utenti_attivi_oggi=utenti_attivi_oggi,
        messaggi_oggi=int(messaggi_oggi),
        totale_messaggi=totale_messaggi,
        per_piano=per_piano,
    )


@router.get("/utenti", response_model=UtentiListOut)
def lista_utenti(db: Session = Depends(get_db)):
    utenti = db.query(Utente).order_by(Utente.creato_il.desc()).all()
    out = []
    for u in utenti:
        msg_oggi = _messaggi_oggi(db, u.id)
        totale_msg = (
            db.query(func.count(Messaggio.id))
            .filter(Messaggio.utente_id == u.id, Messaggio.ruolo == "user")
            .scalar()
            or 0
        )
        out.append(
            UtenteAdminOut(
                email=u.email,
                nome=u.nome,
                cognome=u.cognome or "",
                piano=u.piano,
                attivo=u.attivo,
                messaggi_oggi=msg_oggi,
                limite_giornaliero=_limite_per_piano(u.piano),
                totale_messaggi=totale_msg,
                creato_il=u.creato_il,
            )
        )
    return UtentiListOut(utenti=out)


@router.post("/piano")
def cambia_piano(payload: CambiaPianoIn, db: Session = Depends(get_db)):
    if payload.piano not in PIANI_VALIDI:
        raise HTTPException(status_code=400, detail=f"Piano non valido. Validi: {sorted(PIANI_VALIDI)}")
    utente = db.query(Utente).filter(Utente.email == payload.email).first()
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    utente.piano = payload.piano
    db.commit()
    return {"ok": True, "email": utente.email, "piano": utente.piano}


@router.post("/toggle/{email}")
def toggle_attivo(email: str, db: Session = Depends(get_db)):
    utente = db.query(Utente).filter(Utente.email == email).first()
    if not utente:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    utente.attivo = not utente.attivo
    db.commit()
    return {"ok": True, "email": utente.email, "attivo": utente.attivo}
