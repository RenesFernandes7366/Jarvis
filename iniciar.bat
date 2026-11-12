@echo off
cd /d "%~dp0"
if not exist .venv (
    py -3.12 -m venv .venv || py -3.11 -m venv .venv || py -m venv .venv
    call .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)
python main.py
pause
