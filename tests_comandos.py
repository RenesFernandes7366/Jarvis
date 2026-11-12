"""Teste rápido do interpretador (sem microfone/câmera): python tests_comandos.py"""
from unittest.mock import patch

from jarvis.comandos import Interpretador


class CamFalsa:
    def __init__(self, modo=None):
        self.log, self.modo = [], modo
    @property
    def ativa(self): return self.modo is not None
    def iniciar(self, modo="movimento"): self.log.append(("iniciar", modo)); self.modo = modo
    def parar(self): self.log.append("parar")
    def responder(self, filtro=None): self.log.append(("responder", filtro))


def rodar(frase, modo=None):
    falas, cam, ev = [], CamFalsa(modo), []
    with patch("webbrowser.open", lambda u: ev.append(("web", u))), \
         patch("jarvis.sistema.abrir", lambda a: ev.append(("abrir", a)) or True), \
         patch("jarvis.sistema.fechar", lambda p: ev.append(("fechar", tuple(p))) or True), \
         patch("jarvis.sistema.teclas", lambda *n, repetir=1: ev.append(("teclas", n))), \
         patch("jarvis.sistema.bloquear", lambda: ev.append(("bloquear",))), \
         patch("jarvis.sistema.desligar", lambda reiniciar=False, segundos=30: ev.append(("desligar", reiniciar))), \
         patch("jarvis.sistema.cancelar_desligamento", lambda: ev.append(("cancelar",))):
        i = Interpretador(falas.append, cam)
        i.executar(frase)
    return falas, cam.log, ev, i.sair


assert rodar("abrir navegador")[2] == [("abrir", "https://www.google.com")]
assert rodar("Abrir o YouTube")[2] == [("abrir", "https://www.youtube.com")]
assert rodar("abrir spotify")[2] == [("abrir", "spotify:")]
assert rodar("abrir a calculadora")[2] == [("abrir", "calc")]
assert rodar("abrir pasta downloads")[2] == [("abrir", "%USERPROFILE%\\Downloads")]
assert rodar("fechar spotify")[2] == [("fechar", ("Spotify.exe",))]
assert "q=gatos+fofos" in rodar("pesquisar gatos fofos")[2][0][1]
assert "search_query=musica+relaxante" in rodar("pesquisar musica relaxante no youtube")[2][0][1]
assert rodar("aumentar volume")[2] == [("teclas", ("vol_mais",))]
assert rodar("silenciar")[2] == [("teclas", ("mudo",))]
assert rodar("pausar música")[2] == [("teclas", ("play_pause",))]
assert rodar("próxima música")[2] == [("teclas", ("proxima",))]
assert rodar("minimizar tudo")[2] == [("teclas", ("win", "d"))]
assert rodar("tirar print")[2] == [("teclas", ("win", "printscreen"))]
assert rodar("bloquear computador")[2] == [("bloquear",)]
assert rodar("desligar computador")[2] == [("desligar", False)]
assert rodar("cancelar desligamento")[2] == [("cancelar",)]
assert rodar("ativar câmera")[1] == [("iniciar", "movimento")]
assert rodar("parar câmera")[1] == ["parar"]
assert rodar("encerrar câmera") [1] == ["parar"] and not rodar("encerrar câmera")[3]
assert rodar("contar dedos")[1] == [("iniciar", "dedos")]
assert rodar("quantos dedos estou mostrando", "dedos")[1] == [("responder", None)]
assert rodar("quantos dedos estou mostrando")[1] == [("iniciar", "dedos")]
assert rodar("contar rostos")[1] == [("iniciar", "rostos")]
assert rodar("quantas pessoas tem aqui", "objetos")[1] == [("responder", "pessoa")]
assert rodar("contar objetos")[1] == [("iniciar", "objetos")]
assert rodar("quantos objetos você vê", "objetos")[1] == [("responder", None)]
assert rodar("que horas são")[1] == []
assert rodar("tchau")[3] is True
assert "Não entendi" in rodar("blablabla")[0][0]
assert "comandos.json" in rodar("abrir coisa inexistente")[0][0]
print("OK")
