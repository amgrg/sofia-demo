"""Gestione modello EngGPT2-16B-A3B con supporto mock."""
import logging
import os
import random
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

MODEL_NAME: str = os.getenv("SOFIA_MODEL", "gpt2")
# SOFIA_USE_MOCK=0 per usare il modello reale; di default mock attivo
USE_MOCK: bool = os.getenv("SOFIA_USE_MOCK", "1") != "0"

_pipeline: Optional[Any] = None

# Risposte keyword-based usate sia dal mock sia come fallback del modello reale
_RISPOSTE_KEYWORDS = [
    (
        r"\b(fisco|tasse|f24|iva|partita iva|inps|730|unico)\b",
        "Per la parte fiscale ti conviene partire dal codice tributo esatto sull'F24 — quello dice tutto. "
        "Se è una tassa una tantum (es. registro), versi e basta. Se è ricorrente (es. IVA, INPS), "
        "controlla scadenze: 16 del mese per IVA mensile, fine mese per INPS. "
        "Vuoi che ti aiuti con un caso specifico?",
    ),
    (
        r"\b(superbonus|110|ecobonus|sismabonus|cessione)\b",
        "Il Superbonus al 110% non c'è più dal 2024 — ora è al 70% per condomini e 65% nel 2025. "
        "La cessione del credito è bloccata salvo eccezioni (zone sismiche, ONLUS, IACP). "
        "Per l'unifamiliare devi essere proprietario e residente. Cosa stai pianificando?",
    ),
    (
        r"\b(accertamento|agenzia delle entrate|cartella|equitalia|ader)\b",
        "Hai 60 giorni dalla notifica per agire. Tre strade: "
        "1) paghi con riduzione di 1/3 sulle sanzioni; "
        "2) accertamento con adesione (sospende i termini di 90 giorni); "
        "3) ricorso alla Corte di Giustizia Tributaria. "
        "Prima di tutto verifica la prescrizione e la regolarità della notifica. "
        "Quale anno d'imposta riguarda?",
    ),
    (
        r"\b(contratto|scrivere|lettera|email|preventivo)\b",
        "Dimmi: a chi va e cosa devi ottenere. Per un preventivo basta intestazione, "
        "descrizione voci, importi al netto, IVA, totale lordo, validità (di solito 30 giorni) "
        "e modalità di pagamento. Vuoi che te ne butto giù uno?",
    ),
    (
        r"\b(spid|cie|pec|firma digitale|fatturapa)\b",
        "SPID e CIE sono ormai equivalenti per la PA. La PEC resta obbligatoria per imprese e professionisti. "
        "Per FatturaPA passi da SDI: o usi un portale (Agenzia delle Entrate, gratis, ma scomodo) "
        "o un software di terze parti. Cosa devi fare?",
    ),
    (
        r"\b(ciao|salve|buongiorno|buonasera|hey)\b",
        "Ciao! Sono Sofia. Dimmi pure — fisco, scrittura professionale, normativa, o altro. "
        "Vado dritta al punto.",
    ),
    (r"\b(grazie|ottimo|perfetto|chiaro)\b", "Figurati. Se ti serve altro sono qui."),
    (
        r"\b(chi sei|cosa sei|cosa fai)\b",
        "Sono Sofia, l'assistente AI italiana. Pensata per fisco, burocrazia, "
        "scrittura professionale e tutto quello che riguarda l'Italia. Niente giri di parole.",
    ),
]

_RISPOSTE_GENERICHE = [
    "Capito. Dammi un attimo di contesto in più — di cosa parliamo esattamente?",
    "Interessante. Per risponderti bene mi servirebbe sapere se è un caso personale o aziendale, e l'anno di riferimento.",
    "Posso aiutarti, ma fammi una domanda più concreta — un esempio o una situazione specifica.",
    "Buona domanda. La risposta dipende da un paio di variabili: regime fiscale, tipo di attività, regione. Cosa vale per te?",
]


def _mock_risposta(messaggio: str) -> str:
    testo = messaggio.lower().strip()
    for pattern, risposta in _RISPOSTE_KEYWORDS:
        if re.search(pattern, testo):
            return risposta
    return random.choice(_RISPOSTE_GENERICHE)


def load_model() -> None:
    """Carica EngGPT2-16B-A3B in memoria. In modalità mock non fa nulla."""
    global _pipeline
    if USE_MOCK:
        logger.info("SOFIA_USE_MOCK attivo — EngGPT2-16B-A3B non caricato, risposta mock in uso.")
        return
    try:
        from transformers import pipeline as hf_pipeline  # type: ignore[import]

        logger.info("Caricamento modello %s ...", MODEL_NAME)
        _pipeline = hf_pipeline("text-generation", model=MODEL_NAME)
        logger.info("Modello %s caricato correttamente.", MODEL_NAME)
    except Exception as exc:
        logger.warning(
            "Impossibile caricare %s (%s) — attivo fallback mock.",
            MODEL_NAME,
            exc,
        )
        _pipeline = None


def genera_risposta_sync(messaggio: str) -> str:
    """Genera una risposta sincrona tramite modello o mock."""
    if _pipeline is None:
        return _mock_risposta(messaggio)
    try:
        result = _pipeline(
            messaggio,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            pad_token_id=_pipeline.tokenizer.eos_token_id,
        )
        # restituisce solo il testo generato, senza ripetere il prompt
        generated: str = result[0]["generated_text"]
        if generated.startswith(messaggio):
            generated = generated[len(messaggio):].strip()
        return generated or _mock_risposta(messaggio)
    except Exception as exc:
        logger.warning("Errore durante l'inferenza (%s) — fallback mock.", exc)
        return _mock_risposta(messaggio)
