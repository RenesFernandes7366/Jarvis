"""Testes da escolha de voz e do fallback (sem áudio): python tests_voz.py"""
from types import SimpleNamespace as V
from unittest.mock import patch

from jarvis.voz import Voz, escolher_voz

vozes = [
    V(id="HKEY...\\TTS_MS_EN-US_DAVID_11.0", name="Microsoft David Desktop - English (United States)", languages=[]),
    V(id="HKEY...\\TTS_MS_PT-PT_HELENA_11.0", name="Microsoft Helena Desktop - Portuguese(Portugal)", languages=[]),
    V(id="HKEY...\\TTS_MS_PT-BR_MARIA_11.0", name="Microsoft Maria Desktop - Portuguese(Brazil)", languages=[]),
]
assert escolher_voz(vozes).name.startswith("Microsoft Maria")      # pt-BR vence pt-PT
assert escolher_voz(vozes[:2]).name.startswith("Microsoft Helena")  # sem pt-BR, usa pt-PT
assert escolher_voz(vozes[:1]) is None                              # só inglês

# se o pyttsx3 falhar, cai no PowerShell; o evento "falando" sempre é desligado
v = Voz()
chamadas = []
with patch.object(Voz, "_pyttsx3", side_effect=RuntimeError("boom")), \
     patch.object(Voz, "_powershell", staticmethod(lambda t: chamadas.append(t))):
    v.falar("olá")
assert chamadas == ["olá"] and not v.falando.is_set() and v.fim > 0

# se tudo falhar, não levanta exceção (o Jarvis continua funcionando)
with patch.object(Voz, "_pyttsx3", side_effect=RuntimeError("a")), \
     patch.object(Voz, "_powershell", side_effect=RuntimeError("b")):
    v.falar("olá")
assert not v.falando.is_set()
print("OK")
