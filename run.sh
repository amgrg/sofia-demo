#!/usr/bin/env bash
# Avvio rapido del demo Sofia (Linux/macOS).
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "==> Creo ambiente virtuale .venv"
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installo dipendenze"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Avvio Sofia su http://127.0.0.1:8000"
echo "    Landing : http://127.0.0.1:8000/"
echo "    Demo chat: http://127.0.0.1:8000/demo"
echo "    Admin   : http://127.0.0.1:8000/admin   (admin@sofiaai.it / admin1234)"
echo "    API docs: http://127.0.0.1:8000/api/docs"
echo

exec uvicorn app.main:app --reload --host "${SOFIA_HOST:-127.0.0.1}" --port "${SOFIA_PORT:-8000}"
