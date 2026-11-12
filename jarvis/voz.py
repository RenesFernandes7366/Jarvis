"""Voz do Jarvis (texto -> fala). Teste a sua voz com: python -m jarvis.voz"""
import os
import subprocess
import sys
import threading
import time

AVISO_SEM_PT = (
    "[voz] Nenhuma voz em português instalada: vou falar com a voz padrão (provavelmente em inglês).\n"
    "      Para instalar: Configurações > Hora e idioma > Idioma e região > Adicionar idioma > Português (Brasil),\n"
    "      depois Opções do idioma > Fala (baixar voz). Reinicie o Jarvis."
)


def escolher_voz(vozes):
    """Escolhe a melhor voz em português (pt-BR primeiro, depois pt-PT). None se não houver."""
    melhor, nota = None, 0
    for v in vozes:
        txt = f"{v.id} {v.name} {getattr(v, 'languages', '')}".lower().replace("_", "-")
        n = 3 if ("pt-br" in txt or "brazil" in txt or "brasil" in txt) else 2 if ("portugu" in txt or "pt-pt" in txt) else 0
        if n > nota:
            melhor, nota = v, n
    return melhor


class Voz:
    def __init__(self, taxa=185):
        self.taxa = taxa
        self.falando = threading.Event()  # o microfone ignora o áudio enquanto isto estiver ligado
        self.fim = 0.0  # quando a última fala terminou
        self._avisou = False

    def falar(self, texto: str) -> None:
        print(f"[Jarvis] {texto}")
        self.falando.set()
        try:
            try:
                self._pyttsx3(texto)
            except Exception as e:
                print(f"[voz] pyttsx3 falhou ({e}); tentando o sintetizador do Windows...")
                self._powershell(texto)
        except Exception as e:
            print(f"[voz] Não consegui falar: {e}")
        finally:
            self.fim = time.time()
            self.falando.clear()

    def _pyttsx3(self, texto):
        import pyttsx3

        motor = pyttsx3.init()
        voz = escolher_voz(motor.getProperty("voices"))
        if voz:
            motor.setProperty("voice", voz.id)
        elif not self._avisou:
            self._avisou = True
            print(AVISO_SEM_PT)
        motor.setProperty("rate", self.taxa)
        motor.setProperty("volume", 1.0)
        motor.say(texto)
        motor.runAndWait()

    @staticmethod
    def _powershell(texto):
        if not sys.platform.startswith("win"):
            raise RuntimeError("sem sintetizador de voz disponível")
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "try { $s.SelectVoiceByHints('NotSet','NotSet',0,[Globalization.CultureInfo]'pt-BR') } catch {};"
            "$s.Speak($env:VOZ_TEXTO)"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            env={**os.environ, "VOZ_TEXTO": texto}, check=True, timeout=60,
        )


if __name__ == "__main__":
    import pyttsx3

    print("Vozes instaladas:")
    for v in pyttsx3.init().getProperty("voices"):
        print(f"  - {v.name}  [{v.id}]")
    escolhida = escolher_voz(pyttsx3.init().getProperty("voices"))
    print("Voz escolhida:", escolhida.name if escolhida else "nenhuma em português (usará a padrão)")
    Voz().falar("Olá, eu sou o Jarvis. Se você está me ouvindo, a voz está funcionando.")
