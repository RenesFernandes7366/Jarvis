"""Câmera com detecção de movimento (OpenCV). Roda no thread principal."""
import time
from pathlib import Path

import cv2

JANELA = "Jarvis - Camera (pressione q para parar)"


class DetectorMovimento:
    def __init__(self, falar, pasta="capturas", area_minima=1500, indice_camera=0):
        self.falar = falar
        self.pasta = Path(pasta)
        self.area_minima = area_minima
        self.indice = indice_camera
        self.cap = None
        self.sub = None
        self.ultimo_registro = 0.0

    @property
    def ativa(self) -> bool:
        return self.cap is not None

    def iniciar(self):
        if self.ativa:
            self.falar("A câmera já está ativa.")
            return
        cap = cv2.VideoCapture(self.indice)
        if not cap.isOpened():
            self.falar("Não consegui acessar a câmera.")
            return
        self.cap = cap
        self.sub = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40, detectShadows=False)
        self.pasta.mkdir(exist_ok=True)
        self.falar("Câmera ativada. Detectando movimentos.")

    def parar(self):
        if not self.ativa:
            self.falar("A câmera não está ativa.")
            return
        self._liberar()
        self.falar("Câmera desativada.")

    def _liberar(self):
        self.cap.release()
        self.cap = None
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def passo(self):
        """Processa um frame. Chame em loop enquanto `ativa`."""
        ok, frame = self.cap.read()
        if not ok:
            self._liberar()
            self.falar("Perdi o sinal da câmera.")
            return
        mascara = self.sub.apply(cv2.GaussianBlur(frame, (21, 21), 0))
        mascara = cv2.dilate(cv2.threshold(mascara, 200, 255, cv2.THRESH_BINARY)[1], None, iterations=2)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        movimento = False
        for c in contornos:
            if cv2.contourArea(c) < self.area_minima:
                continue
            movimento = True
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if movimento:
            cv2.putText(frame, "MOVIMENTO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            agora = time.time()
            if agora - self.ultimo_registro > 2:  # no máximo 1 foto a cada 2 s
                self.ultimo_registro = agora
                cv2.imwrite(str(self.pasta / f"mov_{time.strftime('%Y%m%d_%H%M%S')}.jpg"), frame)

        cv2.imshow(JANELA, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.parar()
