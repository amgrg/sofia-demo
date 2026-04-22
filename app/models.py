"""Modelli SQLAlchemy per Sofia."""
from datetime import datetime, date

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Utente(Base):
    __tablename__ = "utenti"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nome = Column(String, nullable=False, default="")
    cognome = Column(String, nullable=True, default="")
    ruolo = Column(String, nullable=False, default="utente")  # 'utente' | 'admin'
    piano = Column(String, nullable=False, default="libero")  # 'libero' | 'professionale' | 'aziende'
    attivo = Column(Boolean, nullable=False, default=True)
    creato_il = Column(DateTime, nullable=False, default=datetime.utcnow)
    ultimo_accesso = Column(DateTime, nullable=True)

    messaggi = relationship("Messaggio", back_populates="utente", cascade="all, delete-orphan")
    uso_giornaliero = relationship("UsoGiornaliero", back_populates="utente", cascade="all, delete-orphan")


class Messaggio(Base):
    __tablename__ = "messaggi"

    id = Column(Integer, primary_key=True, index=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=False, index=True)
    ruolo = Column(String, nullable=False)  # 'user' | 'assistant'
    contenuto = Column(String, nullable=False)
    creato_il = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    utente = relationship("Utente", back_populates="messaggi")


class UsoGiornaliero(Base):
    """Conteggio messaggi-utente per giorno (per limiti piano libero)."""
    __tablename__ = "uso_giornaliero"

    id = Column(Integer, primary_key=True, index=True)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=False, index=True)
    giorno = Column(Date, nullable=False, default=date.today, index=True)
    messaggi = Column(Integer, nullable=False, default=0)

    utente = relationship("Utente", back_populates="uso_giornaliero")
