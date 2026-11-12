@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    py -3.12 -m venv .venv 2>nul || py -3.11 -m venv .venv 2>nul || py -m venv .venv
    if errorlevel 1 goto erro
)
call ".venv\Scripts\activate.bat"

python -c "import speech_recognition, pyaudio, pyttsx3, cv2, mediapipe" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias, aguarde alguns minutos...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 goto erro
)

python main.py
pause
exit /b 0

:erro
echo.
echo *** ERRO na instalacao. Tire um print desta janela e envie para ajuda. ***
pause
exit /b 1
