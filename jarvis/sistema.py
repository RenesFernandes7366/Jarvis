"""Ações do sistema operacional (Windows em primeiro lugar)."""
import ctypes
import os
import subprocess
import sys
import webbrowser

WIN = sys.platform.startswith("win")

VK = {
    "vol_mais": 0xAF, "vol_menos": 0xAE, "mudo": 0xAD,
    "play_pause": 0xB3, "proxima": 0xB0, "anterior": 0xB1,
    "win": 0x5B, "d": 0x44, "printscreen": 0x2C,
}


def teclas(*nomes, repetir=1):
    """Pressiona uma combinação de teclas (ex.: teclas('win', 'd'))."""
    if not WIN:
        return False
    codigos = [VK[n] for n in nomes]
    for _ in range(repetir):
        for c in codigos:
            ctypes.windll.user32.keybd_event(c, 0, 0, 0)
        for c in reversed(codigos):
            ctypes.windll.user32.keybd_event(c, 0, 2, 0)
    return True


def abrir(alvo: str) -> bool:
    """Abre um programa, URL, protocolo (spotify:) ou pasta."""
    alvo = os.path.expandvars(alvo)
    try:
        if WIN:
            subprocess.Popen(f'start "" "{alvo}"', shell=True)
        elif alvo.startswith(("http://", "https://")):
            webbrowser.open(alvo)
        else:
            subprocess.Popen(["xdg-open" if sys.platform != "darwin" else "open", alvo])
        return True
    except OSError:
        return False


def fechar(processos) -> bool:
    """Pede para fechar normalmente (sem /F: o app ainda pergunta se quer salvar)."""
    if not WIN:
        return False
    ok = False
    for p in processos:
        r = subprocess.run(["taskkill", "/IM", p], capture_output=True)
        ok = ok or r.returncode == 0
    return ok


def bloquear() -> bool:
    if WIN:
        ctypes.windll.user32.LockWorkStation()
    return WIN


def desligar(reiniciar=False, segundos=30) -> bool:
    if WIN:
        subprocess.Popen(["shutdown", "/r" if reiniciar else "/s", "/t", str(segundos)])
    return WIN


def cancelar_desligamento() -> bool:
    if WIN:
        subprocess.Popen(["shutdown", "/a"])
    return WIN
