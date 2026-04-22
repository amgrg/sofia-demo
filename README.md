# Sofia AI — Demo locale

Scaffold runnable per il demo Sofia: landing page + chat (mock, offline) + dashboard admin + backend FastAPI con auth JWT e SQLite.

## Struttura cartelle

```
sofia-demo/
├── app/                    Backend FastAPI
│   ├── main.py             Entry point (crea l'app, monta router, seed all'avvio)
│   ├── config.py           Configurazione (env vars con default)
│   ├── database.py         SQLAlchemy engine + sessione
│   ├── models.py           Modelli ORM (Utente, Messaggio, UsoGiornaliero)
│   ├── schemas.py          Schemi Pydantic per request/response
│   ├── auth.py             Hash password (bcrypt) + JWT
│   ├── deps.py             Dependency: get_current_user, require_admin
│   ├── seed.py             Crea admin + utenti demo se DB vuoto
│   └── routers/
│       ├── auth.py         POST /auth/login, /auth/register
│       ├── admin.py        GET /admin/stats, /admin/utenti — POST /admin/piano, /admin/toggle/{email}
│       ├── chat.py         POST /chat (risposte mockate stile Sofia)
│       └── pages.py        GET /, /demo, /admin (HTML)
├── static/                 Pagine HTML
│   ├── landing.html        Homepage marketing
│   ├── demo.html           Chat UI (login + invio messaggi)
│   └── admin.html          Dashboard admin
├── data/                   DB SQLite (creato al primo avvio)
├── requirements.txt        Dipendenze Python
├── .env.example            Template variabili d'ambiente
├── .gitignore
├── Dockerfile              Immagine Python 3.12 slim
├── docker-compose.yml      Orchestratore single-service
├── run.sh                  Avvio rapido (Linux/macOS)
└── run.bat                 Avvio rapido (Windows)
```

## Avvio rapido

### Opzione A — Script

Linux / macOS:

```bash
cd sofia-demo
chmod +x run.sh
./run.sh
```

Windows:

```bat
cd sofia-demo
run.bat
```

Lo script crea un virtualenv, installa le dipendenze e avvia uvicorn su `http://127.0.0.1:8000`.

### Opzione B — Manuale

```bash
cd sofia-demo
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Opzione C — Docker

```bash
cd sofia-demo
docker compose up --build
```

## URL

Una volta avviato:

- Landing page → http://127.0.0.1:8000/
- Chat demo → http://127.0.0.1:8000/demo
- Admin dashboard → http://127.0.0.1:8000/admin
- API docs (Swagger) → http://127.0.0.1:8000/api/docs
- API docs (Redoc) → http://127.0.0.1:8000/api/redoc
- Healthcheck → http://127.0.0.1:8000/healthz

## Credenziali di default (seed)

Al primo avvio il DB SQLite viene popolato con:

- Admin → `admin@sofiaai.it` / `admin1234`
- Utente piano libero → `marco.bianchi@example.it` / `demo1234`
- Utente professionale → `giulia.rossi@example.it` / `demo1234`
- Utente aziende → `studio.legale@example.it` / `demo1234`
- ...altri utenti demo (vedi `app/seed.py`)

Per ricominciare da zero basta eliminare `data/sofia.db` — al riavvio il seed gira di nuovo.

## API principali

| Metodo | Endpoint                    | Descrizione                              | Auth      |
|--------|-----------------------------|------------------------------------------|-----------|
| POST   | `/auth/login`               | Login → restituisce JWT                  | —         |
| POST   | `/auth/register`            | Registrazione nuovo utente               | —         |
| POST   | `/chat`                     | Manda un messaggio, risposta mock        | utente    |
| GET    | `/admin/stats`              | Statistiche dashboard                    | admin     |
| GET    | `/admin/utenti`             | Lista utenti                             | admin     |
| POST   | `/admin/piano`              | Cambia piano utente                      | admin     |
| POST   | `/admin/toggle/{email}`     | Attiva/disabilita utente                 | admin     |

## Pubblicare sul web

Vedi [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) per la guida passo-passo al deploy su Railway (con dominio HTTPS in ~10 minuti).

## Note

- Le risposte della chat sono mockate (regex su parole chiave + risposte hardcoded). Nessuna API esterna richiesta. Per collegare un LLM vero (Claude / OpenAI), modifica `_genera_risposta` in `app/routers/chat.py`.
- Il piano "libero" ha un limite di 30 messaggi al giorno (vedi `LIMITE_GIORNALIERO_LIBERO` in `app/config.py`).
- Tutte le impostazioni sono via variabili d'ambiente — vedi `.env.exa