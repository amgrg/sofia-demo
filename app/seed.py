"""Crea utenti di esempio (admin + alcuni utenti) se il DB è vuoto."""
from datetime import date, datetime, timedelta

from .auth import hash_password
from .config import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from .database import SessionLocal, engine
from .models import Base, Messaggio, UsoGiornaliero, Utente


def seed_if_empty() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Utente).count() > 0:
            return

        # 1. Admin
        admin = Utente(
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            nome="Admin",
            cognome="Sofia",
            ruolo="admin",
            piano="aziende",
            attivo=True,
            creato_il=datetime.utcnow() - timedelta(days=120),
        )
        db.add(admin)

        # 2. Utenti di esempio
        utenti_demo = [
            ("marco.bianchi@example.it", "demo1234", "Marco", "Bianchi", "libero", True, 12, 340, 87),
            ("giulia.rossi@example.it", "demo1234", "Giulia", "Rossi", "professionale", True, 78, 60, 1820),
            ("studio.legale@example.it", "demo1234", "Studio", "Legale Verdi", "aziende", True, 45, 30, 5410),
            ("luca.ferrari@example.it", "demo1234", "Luca", "Ferrari", "libero", True, 28, 15, 215),
            ("anna.colombo@example.it", "demo1234", "Anna", "Colombo", "libero", False, 0, 90, 18),
            ("pmi.bologna@example.it", "demo1234", "PMI", "Bologna Srl", "professionale", True, 134, 7, 980),
        ]

        for email, pw, nome, cognome, piano, attivo, msg_oggi, giorni_fa, totale_msg in utenti_demo:
            u = Utente(
                email=email,
                password_hash=hash_password(pw),
                nome=nome,
                cognome=cognome,
                ruolo="utente",
                piano=piano,
                attivo=attivo,
                creato_il=datetime.utcnow() - timedelta(days=giorni_fa),
            )
            db.add(u)
            db.flush()

            if msg_oggi > 0:
                db.add(UsoGiornaliero(utente_id=u.id, giorno=date.today(), messaggi=msg_oggi))

            # finto storico messaggi (solo conteggio "user" per la colonna "Totale msg")
            for _ in range(totale_msg):
                db.add(Messaggio(utente_id=u.id, ruolo="user", contenuto="..."))

        db.commit()
        print(f"[seed] Creato admin {DEFAULT_ADMIN_EMAIL} (password: {DEFAULT_ADMIN_PASSWORD})")
        print(f"[seed] Creati {len(utenti_demo)} utenti di esempio (password: demo1234)")
    finally:
        db.close()


if __name__ == "__main__":
    seed_if_empty()
