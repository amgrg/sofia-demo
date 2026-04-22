@echo off
REM Avvio rapido del demo Sofia (Windows).
cd /d "%~dp0"

if not exist .venv (
  echo ==^> Creo ambiente virtuale .venv
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo ==^> Installo dipendenze
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo.
echo ==^> Avvio Sofia su http://127.0.0.1:8000
echo     Landing  : http://127.0.0.1:8000/
echo     Demo chat: http://127.0.0.1:8000/demo
echo     Admin    : http://127.0.0.1:8000/admin   (admin@sofiaai.it / admin1234)
echo     API docs : http://127.0.0.1:8000/api/docs
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
