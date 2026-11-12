"""Jarvis: assistente de voz. Execute: python main.py"""
import queue
import sys
import threading
import time

import speech_recognition as sr

from jarvis.comandos import Interpretador, normalizar
from jarvis.camera import Camera
from jarvis.voz import Voz

IDIOMA = "pt-BR"
PALAVRA_DE_ATIVACAO = "jarvis"  # fale "Jarvis, abrir navegador". Use "" para aceitar qualquer frase.

if hasattr(sys.stdout, "reconfigure"):  # acentos corretos no terminal do Windows
    sys.stdout.reconfigure(encoding="utf-8")

voz = Voz()
falar = voz.falar
pronto = threading.Event()  # o microfone terminou de calibrar


def escutar(fila: queue.Queue, parar: threading.Event) -> None:
    rec = sr.Recognizer()
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic, duration=1)
        print("Pronto! Diga: 'Jarvis, abrir navegador' ou 'Jarvis, ativar câmera'.")
        pronto.set()
        while not parar.is_set():
            if voz.falando.is_set():  # não escuta enquanto o Jarvis fala
                time.sleep(0.1)
                continue
            inicio = time.time()
            try:
                audio = rec.listen(mic, timeout=3, phrase_time_limit=8)
                if voz.falando.is_set() or voz.fim > inicio:
                    continue  # a gravação pegou a própria voz do Jarvis
                texto = rec.recognize_google(audio, language=IDIOMA)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                continue
            except sr.RequestError as e:
                print(f"Erro no serviço de reconhecimento: {e}")
                continue
            print(f"[Você] {texto}")
            fila.put(texto)


def main() -> None:
    fila: queue.Queue = queue.Queue()
    parar = threading.Event()
    camera = Camera(falar)
    interp = Interpretador(falar, camera)
    threading.Thread(target=escutar, args=(fila, parar), daemon=True).start()

    saudou = False
    try:
        while not interp.sair:
            if pronto.is_set() and not saudou:  # a voz sempre é usada no thread principal
                saudou = True
                falar("Jarvis pronto. Pode falar.")
            try:
                # com a câmera ativa não bloqueia, para manter o vídeo fluindo
                texto = fila.get(timeout=0.001 if camera.ativa else 0.2)
            except queue.Empty:
                texto = None
            if texto:
                t = normalizar(texto)
                if not PALAVRA_DE_ATIVACAO or t.startswith(PALAVRA_DE_ATIVACAO):
                    interp.executar(t.removeprefix(PALAVRA_DE_ATIVACAO).strip(" ,"))
            if camera.ativa:
                camera.passo()
    except KeyboardInterrupt:
        pass
    finally:
        parar.set()
        if camera.ativa:
            camera.parar()


if __name__ == "__main__":
    main()
