# Deploy del demo Sofia su Railway

Guida passo-passo per pubblicare il demo su un URL pubblico (es. `sofia-demo-production.up.railway.app`) in circa 10-15 minuti.

## Cosa ti serve

- Un account [GitHub](https://github.com) (gratis)
- Un account [Railway](https://railway.com) (gratis, serve carta di credito per la verifica anche se resti nel free tier ~$5/mese)
- Git installato sulla tua macchina

## 1. Metti il progetto su GitHub

Da terminale, dentro la cartella `sofia-demo`:

```bash
cd sofia-demo
git init
git add .
git commit -m "Sofia demo — primo deploy"
```

Poi crea un repo nuovo su GitHub (vuoto, senza README) e collega:

```bash
git remote add origin https://github.com/TUO-USERNAME/sofia-demo.git
git branch -M main
git push -u origin main
```

> Suggerito: tieni il repo **privato** finché non hai cambiato `SOFIA_SECRET_KEY` e `SOFIA_ADMIN_PASSWORD`.

## 2. Crea il progetto su Railway

1. Vai su [railway.com/new](https://railway.com/new) → **Deploy from GitHub repo**.
2. Autorizza Railway a leggere i tuoi repo.
3. Seleziona `sofia-demo`.
4. Railway vede il `Dockerfile` e il `railway.json` e parte automaticamente con il build.

Aspetta ~2-3 minuti il primo build. Vedrai i log nella tab **Deployments**.

## 3. Aggiungi il volume persistente per SQLite

Senza questo passo, il DB SQLite viene cancellato a ogni redeploy.

1. Nel servizio appena creato → tab **Settings** → sezione **Volumes** → **Create Volume**.
2. **Mount path**: `/app/data`
3. **Size**: 1 GB basta e avanza.
4. Salva. Railway fa redeploy automatico.

Da questo momento il file `data/sofia.db` sopravvive a tutti i restart.

## 4. Imposta le variabili d'ambiente (importante per la sicurezza)

Tab **Variables** → aggiungi:

| Nome                   | Valore                                       |
|------------------------|----------------------------------------------|
| `SOFIA_SECRET_KEY`     | Stringa lunga e casuale (vedi sotto)         |
| `SOFIA_ADMIN_EMAIL`    | La tua email (es. `tu@esempio.it`)           |
| `SOFIA_ADMIN_PASSWORD` | Una password forte (NON `admin1234`!)         |

Per generare una `SECRET_KEY` solida:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

> Se cambi `SOFIA_ADMIN_EMAIL` o `SOFIA_ADMIN_PASSWORD` dopo il primo deploy, il seed non li riapplica perché il DB è già popolato. Per ripartire da zero: cancella il volume e ricrealo.

## 5. Esponi al pubblico

Tab **Settings** → **Networking** → **Generate Domain**.

Railway ti dà un URL tipo `sofia-demo-production-1a2b.up.railway.app`. Apri:

- `https://<dominio>/` → landing
- `https://<dominio>/demo` → chat
- `https://<dominio>/admin` → dashboard
- `https://<dominio>/api/docs` → Swagger

HTTPS è automatico.

## 6. (Opzionale) Dominio personalizzato

Se hai un dominio (es. `sofiaai.it`):

1. **Settings** → **Networking** → **Custom Domain** → inserisci `demo.sofiaai.it`.
2. Railway ti mostra un record CNAME — aggiungilo dal pannello del tuo registrar.
3. Aspetta la propagazione (5-30 minuti). HTTPS arriva da solo via Let's Encrypt.

## Aggiornamenti

Ogni `git push` sul branch `main` triggera un nuovo deploy automatico. Zero downtime.

Per fare rollback: tab **Deployments** → trovi il deploy precedente → **Redeploy**.

## Costi

- Free trial: $5 di credito al mese.
- Un container piccolo come questo consuma ~$0.50-2/mese se ha poco traffico.
- Volume da 1 GB: $0.25/mese.
- Quando finiscono i $5 ti chiede di passare al piano Hobby ($5 fissi/mese + consumo).

## Quando passare a Postgres

SQLite va bene fino a ~50-100 utenti concorrenti. Quando senti che è il momento:

1. **Aggiungi Postgres**: Railway → **+ New** → **Database** → **Add PostgreSQL**.
2. Railway crea automaticamente la variabile `DATABASE_URL`.
3. Modifica `app/config.py`:
   ```python
   DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SOFIA_DATABASE_URL", f"sqlite:///{DATA_DIR / 'sofia.db'}")
   ```
4. Aggiungi a `requirements.txt`: `psycopg[binary]==3.2.3`
5. Push → redeploy.

Lo schema viene creato automaticamente da SQLAlchemy al primo avvio. Per migrare i dati esistenti da SQLite a Postgres serve un piccolo script — quando ci arrivi, te lo preparo.

## Troubleshooting

**Build fallisce con "no module named X"** → controlla `requirements.txt`, fai commit, ripush.

**App parte ma 502 Bad Gateway** → Railway non sta ricevendo risposta sul `$PORT`. Verifica che il `CMD` del Dockerfile usi `${PORT:-8000}`.

**Healthcheck fallisce** → controlla che `/healthz` risponda 200. Aumenta `healthcheckTimeout` in `railway.json` se l'avvio è lento.

**Login admin fallisce** → hai cambiato `SOFIA_ADMIN_PASSWORD` dopo il primo deploy. Cancella il volume e riavvia.
