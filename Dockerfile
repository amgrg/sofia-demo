FROM python:3.12-slim

WORKDIR /app

# Dipendenze di sistema minime per bcrypt/cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static

# Cartella runtime per il DB SQLite (volume in compose)
RUN mkdir -p /app/data
VOLUME ["/app/data"]

ENV SOFIA_HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

# Railway/Fly/Render iniettano $PORT a runtime — sh -c serve per espandere 