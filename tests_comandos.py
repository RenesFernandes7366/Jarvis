"""Teste rápido do interpretador (sem microfone/câmera): python tests_comandos.py"""
from unittest.mock import patch

from jarvis.comandos import Interpretador


class CamFalsa:
    def __init__(self): self.log = []
    def iniciar(self): self.log.append("iniciar")
    def parar(self): self.log.append("parar")


def rodar(frase):
    falas, cam = [], CamFalsa()
    with patch("webbrowser.open") as wb:
        i = Interpretador(falas.append, cam)
        i.executar(frase)
    return falas, cam.log, [c.args[0] for c in wb.call_args_list], i.sair


assert rodar("abrir navegador")[2] == ["https://www.google.com"]
assert rodar("Abrir o YouTube")[2] == ["https://www.youtube.com"]
assert "q=gatos+fofos" in rodar("pesquisar gatos fofos")[2][0]
assert rodar("ativar câmera")[1] == ["iniciar"]
assert rodar("iniciar detecção de movimento")[1] == ["iniciar"]
assert rodar("parar câmera")[1] == ["parar"]
assert rodar("desativar a câmera")[1] == ["parar"]
assert rodar("tchau")[3] is True
assert "Não entendi" in rodar("blablabla")[0][0]
print("OK")
