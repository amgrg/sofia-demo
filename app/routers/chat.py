"""Endpoint /chat — risposte mockate (offline) in stile Sofia."""
import random
import re
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import LIMITE_GIORNALIERO_LIBERO
from ..database import get_db
from ..deps import get_current_user
from ..models import Messaggio, UsoGiornaliero, Utente
from ..schemas import ChatIn, ChatOut

router = APIRouter(prefix="/chat", tags=["chat"])

# Risposte mockate "in stile Sofia": brevi, chiare, italiane.
RISPOSTE_KEYWORDS = [
    (r"\b(fisco|tasse|f24|iva|partita iva|inps|730|unico)\b",
     "Per la parte fiscale ti conviene partire dal codice tributo esatto sull'F24 — quello dice tutto. Se è una tassa una tantum (es. registro), versi e basta. Se è ricorrente (es. IVA, INPS), controlla scadenze: 16 del mese per IVA mensile, fine mese per INPS. Vuoi che ti aiuti con un caso specifico?"),
    (r"\b(superbonus|110|ecobonus|sismabonus|cessione)\b",
     "Il Superbonus al 110% non c'è più dal 2024 — ora è al 70% per condomini e 65% nel 2025. La cessione del credito è bloccata salvo eccezioni (zone sismiche, ONLUS, IACP). Per l'unifamiliare devi essere proprietario e residente. Cosa stai pianificando?"),
    (r"\b(accertamento|agenzia delle entrate|cartella|equitalia|ader)\b",
     "Hai 60 giorni dalla notifica per agire. Tre strade: 1) paghi con riduzione di 1/3 sulle sanzioni; 2) accertamento con adesione (sospende i termini di 90 giorni); 3) ricorso alla Corte di Giustizia Tributaria. Prima di tutto verifica la prescrizione e la regolarità della notifica. Quale anno d'imposta riguarda?"),
    (r"\b(contratto|scrivere|lettera|email|preventivo)\b",
     "Dimmi: a chi va e cosa devi ottenere. Per un preventivo basta intestazione, descrizione voci, importi al netto, IVA, totale lordo, validità (di solito 30 giorni) e modalità di pagamento. Vuoi che te ne butto giù uno?"),
    (r"\b(spid|cie|pec|firma digitale|fatturapa)\b",
     "SPID e CIE sono ormai equivalenti per la PA. La PEC resta obbligatoria per imprese e professionisti. Per FatturaPA passi da SDI: o usi un portale (Agenzia delle Entrate, gratis, ma scomodo) o un software di terze parti. Cosa devi fare?"),
    (r"\b(ciao|salve|buongiorno|buonasera|hey)\b",
     "Ciao! Sono Sofia. Dimmi pure — fisco, scrittura professionale, normativa, o altro. Vado dritta al punto."),
    (r"\b(grazie|ottimo|perfetto|chiaro)\b",
     "Figurati. Se ti serve altro sono qui."),
    (r"\b(chi sei|cosa sei|cosa fai)\b",
     "Sono Sofia, l'assistente AI italiana. Pensata per fisco, burocrazia, scrittura professionale e tutto quello che riguarda l'Italia. Niente giri di parole."),
]

RISPOSTE_GENERICHE = [
    "Capito. Dammi un attimo di contesto in più — di cosa parliamo esattamente?",
    "Interessante. Per risponderti bene mi servirebbe sapere se è un caso personale o aziendale, e l'anno di riferimento.",
    "Posso aiutarti, ma fammi una domanda più concreta — un esempio o una situazione specifica.",
    "Buona domanda. La risposta dipende da un paio di variabili: regime fiscale, tipo di attività, regione. Cosa vale per te?",
]


def _genera_risposta(messaggio: str) -> str:
    testo = messaggio.lower().strip()
    for pattern, risposta in RISPOSTE_KEYWORDS:
        if re.search(pattern, testo):
            return risposta
    return random.choice(RISPOSTE_GENERICHE)


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

    # Genera risposta mock
    risposta = _genera_risposta(payload.messaggio)
    db.add(Messaggio(utente_id=utente.id, ruolo="assistant", contenuto=risposta))

    uso.messaggi += 1
    db.commit()

    return ChatOut(
        risposta=risposta,
        messaggi_oggi=uso.messaggi,
        limite_giornaliero=limite,
    )
