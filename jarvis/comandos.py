"""Interpretação de frases e ações do sistema (abrir apps, sites, pesquisas)."""
import json
import re
import unicodedata
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

from . import sistema


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


def carregar_config() -> dict:
    caminho = Path(__file__).resolve().parent.parent / "comandos.json"
    with open(caminho, encoding="utf-8") as f:
        cfg = json.load(f)
    # normaliza as chaves (sem acento/maiúscula) para casar com a fala
    return {sec: {normalizar(k): v for k, v in dados.items()} for sec, dados in cfg.items()}


class Interpretador:
    """Transforma texto falado em ação. `falar` e `camera` são injetados pelo main."""

    def __init__(self, falar, camera, config=None):
        self.falar = falar
        self.camera = camera
        self.cfg = config if config is not None else carregar_config()
        self.sair = False

    # ---- ações ----
    def _abrir(self, alvo: str) -> None:
        alvo = re.sub(r"^pasta (de |do |da )?", "", alvo)
        apps, sites, pastas = self.cfg["apps"], self.cfg["sites"], self.cfg["pastas"]
        if alvo in ("browser", "internet"):
            alvo = "navegador"
        if alvo in apps:
            ok = sistema.abrir(apps[alvo]["abrir"])
        elif alvo in sites:
            ok = sistema.abrir(sites[alvo])
        elif alvo in pastas:
            ok = sistema.abrir(pastas[alvo])
        else:
            self.falar(f"Não sei abrir {alvo}. Adicione no arquivo comandos.json.")
            return
        self.falar(f"Abrindo {alvo}" if ok else f"Não consegui abrir {alvo}")

    def _fechar(self, alvo: str) -> None:
        app = self.cfg["apps"].get(alvo)
        if not app or not app.get("processo"):
            self.falar(f"Não sei fechar {alvo}.")
        elif sistema.fechar(app["processo"]):
            self.falar(f"Fechando {alvo}")
        else:
            self.falar(f"{alvo} não parece estar aberto.")

    # ---- interpretação ----
    def executar(self, frase: str) -> None:
        t = normalizar(frase)
        if not t:
            return
        busca = re.search(r"(?:pesquisar|pesquise|buscar|busque|procurar) (?:por |sobre )?(.+)", t)

        # câmera (antes de "sair"/"fechar" para "encerrar câmera" não fechar o Jarvis)
        if re.search(r"(parar|desativar|desligar|encerrar|fechar) (a )?(camera|deteccao|monitoramento)", t):
            self.camera.parar()
        elif re.search(r"(ativar|ligar|iniciar|abrir|comecar) (a )?(camera|deteccao|monitoramento|captura)", t) or (
            "camera" in t and "movimento" in t
        ):
            self.camera.iniciar()
        elif re.search(r"\b(sair|tchau|desligar jarvis)\b", t):
            self.falar("Até logo!")
            self.sair = True

        # sistema
        elif re.search(r"(aumentar|subir|mais) (o )?volume|volume (mais|alto)", t):
            sistema.teclas("vol_mais", repetir=5)
            self.falar("Volume aumentado")
        elif re.search(r"(diminuir|abaixar|baixar|menos) (o )?volume|volume (menos|baixo)", t):
            sistema.teclas("vol_menos", repetir=5)
            self.falar("Volume diminuído")
        elif re.search(r"\b(silenciar|mutar|tirar o som|ativar mudo)\b", t):
            sistema.teclas("mudo")
            self.falar("Som alternado")
        elif re.search(r"proxima (musica|faixa)|pular (a )?(musica|faixa)", t):
            sistema.teclas("proxima")
        elif re.search(r"(musica|faixa) anterior|voltar (a )?(musica|faixa)", t):
            sistema.teclas("anterior")
        elif re.search(r"\b(pausar|continuar|retomar|despausar|tocar|dar play)\b", t) and "youtube" not in t and not busca:
            sistema.teclas("play_pause")
            self.falar("Ok")
        elif re.search(r"minimizar tudo|mostrar (a )?area de trabalho", t):
            sistema.teclas("win", "d")
        elif re.search(r"(tirar|fazer) (um )?(print|captura)|captura de tela", t):
            sistema.teclas("win", "printscreen")
            self.falar("Captura salva na pasta Imagens, Capturas de tela")
        elif re.search(r"(bloquear|travar) (o )?(computador|pc|tela)", t):
            self.falar("Bloqueando")
            sistema.bloquear()
        elif re.search(r"cancelar (o )?(desligamento|reinicio|reiniciar)", t):
            sistema.cancelar_desligamento()
            self.falar("Desligamento cancelado")
        elif re.search(r"reiniciar (o )?(computador|pc)", t):
            self.falar("Reiniciando em 30 segundos. Diga cancelar desligamento para parar.")
            sistema.desligar(reiniciar=True)
        elif re.search(r"desligar (o )?(computador|pc)", t):
            self.falar("Desligando em 30 segundos. Diga cancelar desligamento para parar.")
            sistema.desligar()

        # internet / programas
        elif m := re.search(r"(?:pesquisar|pesquise|buscar|busque|procurar|tocar|ver) (?:por |sobre )?(.+?) no youtube", t) or (
            re.search(r"youtube (?:pesquisar|buscar|procurar) (.+)", t)
        ):
            self.falar(f"Procurando {m.group(1)} no YouTube")
            webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(m.group(1)))
        elif busca:
            self.falar(f"Pesquisando {busca.group(1)}")
            webbrowser.open("https://www.google.com/search?q=" + quote_plus(busca.group(1)))
        elif m := re.search(r"(?:abrir|abra|iniciar|executar) (?:o |a |os |as )?(.+)", t):
            self._abrir(m.group(1))
        elif m := re.search(r"(?:fechar|feche) (?:o |a )?(.+)", t):
            self._fechar(m.group(1))

        elif "horas" in t:
            self.falar("São " + datetime.now().strftime("%H:%M"))
        elif "ajuda" in t or "comandos" in t:
            self.falar(
                "Posso abrir e fechar programas, sites e pastas, pesquisar, controlar volume e música, "
                "tirar print, bloquear o computador e ativar a câmera para detectar movimento."
            )
        else:
            self.falar("Não entendi o comando.")
