# Sofia AI — Demo locale

Scaffold runnable del progetto **Sofia**: landing page marketing + chat AI (mock o modello reale) + dashboard admin, con backend **FastAPI**, autenticazione **JWT** e database **SQLite**.

Pensato per consentire a un nuovo collaboratore di avere l'ambiente funzionante in meno di 5 minuti.

---

## Indice

- [Prerequisiti](#prerequisiti)
- [Struttura del progetto](#struttura-del-progetto)
- [Avvio rapido](#avvio-rapido)
- [Variabili d'ambiente](#variabili-dambiente)
- [Credenziali di default](#credenziali-di-default)
- [URL e pagine](#url-e-pagine)
- [API reference](#api-reference)
- [Modalità mock vs modello reale](#modalità-mock-vs-modello-reale)
- [Piani e limiti](#piani-e-limiti)
- [Come estendere il progetto](#come-estendere-il-progetto)
- [Deploy su Railway](#deploy-su-railway)
- [Workflow git](#workflow-git)

---

## Prerequisiti

| Strumento | Versione minima | Note |
|-----------|----------------|------|
| Python | 3.10+ | consigliato 3.12 |
| pip | qualsiasi | incluso con Python |
| Docker + Docker Compose | qualsiasi | solo per Opzione C |
| git | qualsiasi | — |

Non è richiesta nessuna API key esterna: di default la chat usa risposte **mock** offline.

---

## Struttura del progetto

```
sofia-demo/
├── app/                        Backend FastAPI
│   ├── main.py                 Entry point: crea l'app, registra i router, esegue seed e carica il modello
│   ├── config.py               Configurazione centralizzata (env vars con default)
│   ├── database.py             SQLAlchemy engine + sessione
│   ├── models.py               ORM: Utente, Messaggio, UsoGiornaliero
│   ├── schemas.py              Schemi Pydantic per request/response
│   ├── auth.py                 Hash password (bcrypt) + generazione/verifica JWT
│   ├── deps.py                 Dipendenze FastAPI: get_current_user, require_admin
│   ├── model.py                Wrapper modello AI (mock keyword-based o HuggingFace reale)
│   ├── seed.py                 Popola il DB con admin + utenti demo al primo avvio
│   └── routers/
│       ├── auth.py             POST /auth/login, /auth/register
│       ├── admin.py            Endpoint dashboard admin (stats, utenti, piani)
│       ├── chat.py             POST /chat — genera risposta mock o da modello
│       └── pages.py            Serve le pagine HTML
├── static/                     Frontend HTML (no build step)
│   ├── landing.html            Homepage marketing
│   ├── demo.html               Chat UI (login + invio messaggi)
│   └── admin.html              Dashboard admin
├── data/                       DB SQLite — creato automaticamente al primo avvio
├── requirements.txt            Dipendenze Python
├── .env.example                Template variabili d'ambiente → copiare in .env
├── .gitignore
├── Dockerfile                  Immagine Python 3.12-slim
├── docker-compose.yml          Orchestratore single-service con volume per il DB
├── railway.json                Configurazione deploy Railway
├── run.sh                      Avvio rapido Linux/macOS
├── run.bat                     Avvio rapido Windows
└── RAILWAY_DEPLOY.md           Guida deploy su Railway
```

---

## Avvio rapido

Clona il repository se non l'hai già fatto:

```bash
git clone https://github.com/amgrg/sofia-demo.git
cd sofia-demo
```

Scegli una delle tre opzioni:

### Opzione A — Script (consigliata per sviluppo)

**Linux / macOS:**

```bash
chmod +x run.sh
./run.sh
```

**Windows:**

```bat
run.bat
```

Lo script crea automaticamente un virtualenv `.venv`, installa le dipendenze e avvia uvicorn in modalità `--reload` su `http://127.0.0.1:8000`.

---

### Opzione B — Manuale

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

### Opzione C — Docker

```bash
docker compose up --build
```

Il volume `sofia-data` persiste il DB SQLite tra i riavvii del container.

---

## Variabili d'ambiente

Tutte le variabili hanno valori di default funzionanti per lo sviluppo locale. Per personalizzarle copia `.env.example` in `.env` e modifica i valori.

```bash
cp .env.example .env
```

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `SOFIA_HOST` | `127.0.0.1` | Host su cui uvicorn si mette in ascolto (`0.0.0.0` in produzione) |
| `SOFIA_PORT` | `8000` | Porta |
| `SOFIA_SECRET_KEY` | *(stringa demo)* | Chiave HMAC per i JWT — **cambiare in produzione** |
| `SOFIA_JWT_EXPIRE_MINUTES` | `1440` | Durata token JWT in minuti (default 24h) |
| `SOFIA_ADMIN_EMAIL` | `admin@sofiaai.it` | Email admin creata dal seed |
| `SOFIA_ADMIN_PASSWORD` | `admin1234` | Password admin creata dal seed — **cambiare in produzione** |
| `SOFIA_DATABASE_URL` | `sqlite:///./data/sofia.db` | URL database SQLAlchemy |
| `SOFIA_MODEL` | `gpt2` | Nome modello HuggingFace usato se mock disattivato |
| `SOFIA_USE_MOCK` | `1` | `1` = risposte mock offline, `0` = carica il modello reale |

> **Nota sicurezza:** non committare mai un file `.env` con valori reali. Il `.gitignore` lo esclude già.

---

## Credenziali di default

Al primo avvio il DB viene popolato automaticamente da `app/seed.py`:

| Ruolo | Email | Password | Piano |
|-------|-------|----------|-------|
| Admin | `admin@sofiaai.it` | `admin1234` | — |
| Utente demo | `marco.bianchi@example.it` | `demo1234` | Libero |
| Utente demo | `giulia.rossi@example.it` | `demo1234` | Professionale |
| Utente demo | `studio.legale@example.it` | `demo1234` | Aziende |

Per **azzerare il DB** ed eseguire di nuovo il seed:

```bash
rm data/sofia.db
# poi riavvia il server
```

---

## URL e pagine

Con il server avviato su `http://127.0.0.1:8000`:

| Pagina | URL |
|--------|-----|
| Landing page | http://127.0.0.1:8000/ |
| Chat demo | http://127.0.0.1:8000/demo |
| Admin dashboard | http://127.0.0.1:8000/admin |
| Swagger UI | http://127.0.0.1:8000/api/docs |
| Redoc | http://127.0.0.1:8000/api/redoc |
| Healthcheck | http://127.0.0.1:8000/healthz |

---

## API reference

### Autenticazione

| Metodo | Endpoint | Body | Auth | Descrizione |
|--------|----------|------|------|-------------|
| `POST` | `/auth/login` | `{email, password}` | — | Restituisce JWT |
| `POST` | `/auth/register` | `{email, password, nome}` | — | Registra nuovo utente (piano libero) |

Il JWT va inviato come `Authorization: Bearer <token>` in tutte le richieste autenticate.

### Chat

| Metodo | Endpoint | Body | Auth | Descrizione |
|--------|----------|------|------|-------------|
| `POST` | `/chat` | `{messaggio}` | utente | Invia messaggio, riceve risposta AI |

Il piano libero è limitato a **30 messaggi/giorno** (vedi `LIMITE_GIORNALIERO_LIBERO` in `app/config.py`).

### Admin

| Metodo | Endpoint | Body | Auth | Descrizione |
|--------|----------|------|------|-------------|
| `GET` | `/admin/stats` | — | admin | Statistiche generali dashboard |
| `GET` | `/admin/utenti` | — | admin | Lista completa utenti |
| `POST` | `/admin/piano` | `{email, piano}` | admin | Cambia piano di un utente |
| `POST` | `/admin/toggle/{email}` | — | admin | Attiva / disabilita utente |

---

## Modalità mock vs modello reale

Di default `SOFIA_USE_MOCK=1`: nessun modello viene caricato, le risposte vengono generate tramite **regex su parole chiave** (fisco, superbonus, SPID, ecc.) definite in `app/model.py`.

Per usare un modello **HuggingFace** reale:

```bash
# Nel .env
SOFIA_USE_MOCK=0
SOFIA_MODEL=gpt2          # sostituisci con il modello che vuoi
```

Installa le dipendenze aggiuntive:

```bash
pip install transformers torch
```

Per collegare invece **Claude o OpenAI**, modifica la funzione `genera_risposta_sync` in `app/model.py` sostituendo la chiamata al pipeline HuggingFace con la chiamata all'API desiderata.

---

## Piani e limiti

| Piano | Limite giornaliero messaggi |
|-------|---------------------------|
| Libero | 30 |
| Professionale | illimitato |
| Aziende | illimitato |

Il limite è gestito in `app/routers/chat.py` tramite il modello `UsoGiornaliero` in SQLite. Per modificare la soglia del piano libero aggiorna `LIMITE_GIORNALIERO_LIBERO` in `app/config.py`.

---

## Come estendere il progetto

**Aggiungere un nuovo router:**

1. Crea `app/routers/nuovo.py` con un `APIRouter`.
2. Importalo e registralo in `app/main.py` con `app.include_router(...)`.

**Aggiungere un modello ORM:**

1. Definisci la classe in `app/models.py` (eredita da `Base`).
2. Il DB viene creato automaticamente da `database.py` con `Base.metadata.create_all`.

**Aggiungere utenti demo al seed:**

Modifica la lista in `app/seed.py`.

**Aggiungere una pagina HTML:**

Aggiungi il file in `static/` e una route in `app/routers/pages.py`.

---

## Deploy su Railway

Vedi [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) per la guida completa (dominio HTTPS in ~10 minuti).

In sintesi:

```bash
# Dalla root del progetto
railway login
railway up
```

Railway rileva automaticamente il `Dockerfile` e inietta la variabile `PORT` a runtime.

---

## Workflow git

Il branch principale è `main`. Per contribuire:

```bash
git checkout -b feat/nome-feature
# lavora, committa
git push origin feat/nome-feature
# apri una Pull Request verso main
```

Convenzioni commit: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`.

Nessuna pipeline CI configurata al momento — i test manuali vanno fatti prima di aprire la PR.
