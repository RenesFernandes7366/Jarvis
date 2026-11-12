"""Interpretação de frases e ações do sistema (abrir apps, sites, pesquisas)."""
import re
import subprocess
import sys
import unicodedata
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


SITES = {
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "whatsapp": "https://web.whatsapp.com",
    "google": "https://www.google.com",
}

# nome falado -> comando por sistema operacional
APPS = {
    "calculadora": {"win32": "calc", "darwin": "open -a Calculator", "linux": "gnome-calculator"},
    "bloco de notas": {"win32": "notepad", "darwin": "open -a TextEdit", "linux": "gedit"},
    "terminal": {"win32": "start cmd", "darwin": "open -a Terminal", "linux": "x-terminal-emulator"},
    "explorador": {"win32": "start explorer", "darwin": "open .", "linux": "xdg-open ."},
}


def _plataforma() -> str:
    return "win32" if sys.platform.startswith("win") else "darwin" if sys.platform == "darwin" else "linux"


def abrir_app(nome: str) -> bool:
    cmd = APPS.get(nome, {}).get(_plataforma())
    if not cmd:
        return False
    try:
        if _plataforma() == "win32":
            subprocess.Popen(cmd, shell=True)  # calc, notepad, "start cmd"...
        else:
            subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


class Interpretador:
    """Transforma texto falado em ação. `falar` e `camera` são injetados pelo main."""

    def __init__(self, falar, camera):
        self.falar = falar
        self.camera = camera
        self.sair = False

    def executar(self, frase: str) -> None:
        t = normalizar(frase)
        if not t:
            return

        if any(p in t for p in ("sair", "encerrar", "tchau", "desligar jarvis")):
            self.falar("Até logo!")
            self.sair = True
        elif re.search(r"(parar|desativar|desligar|encerrar|fechar) (a )?(camera|deteccao|monitoramento)", t):
            self.camera.parar()
        elif re.search(r"(ativar|ligar|iniciar|abrir|comecar) (a )?(camera|deteccao|monitoramento|captura)", t) or (
            "camera" in t and "movimento" in t
        ):
            self.camera.iniciar()
        elif m := re.search(r"(?:pesquisar|pesquise|buscar|busque|procurar) (?:por |sobre )?(.+)", t):
            self.falar(f"Pesquisando {m.group(1)}")
            webbrowser.open("https://www.google.com/search?q=" + quote_plus(m.group(1)))
        elif m := re.search(r"abrir (?:o |a )?(.+)", t):
            alvo = m.group(1)
            if alvo in ("navegador", "browser", "chrome", "firefox"):
                self.falar("Abrindo o navegador")
                webbrowser.open("https://www.google.com")
            elif alvo in SITES:
                self.falar(f"Abrindo {alvo}")
                webbrowser.open(SITES[alvo])
            elif alvo in APPS and abrir_app(alvo):
                self.falar(f"Abrindo {alvo}")
            else:
                self.falar(f"Não sei abrir {alvo}")
        elif "horas" in t or "hora e" in t:
            self.falar("São " + datetime.now().strftime("%H:%M"))
        elif "ajuda" in t or "comandos" in t:
            self.falar(
                "Posso abrir o navegador, sites, aplicativos, pesquisar na internet, "
                "dizer as horas e ativar a câmera para detectar movimento."
            )
        else:
            self.falar("Não entendi o comando.")
