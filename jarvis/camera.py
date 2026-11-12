"""Câmera com vários modos: movimento, dedos, rostos e objetos (OpenCV + MediaPipe).

Tudo roda no thread principal (exigência do cv2.imshow). Os modelos de IA do
MediaPipe são baixados automaticamente na primeira vez (alguns MB) para a pasta modelos/.
"""
import sys
import time
import urllib.request
from collections import Counter, deque
from math import hypot
from pathlib import Path

import cv2

JANELA = "Jarvis - Camera (pressione q para parar)"
PASTA_MODELOS = Path(__file__).resolve().parent.parent / "modelos"
_BASE = "https://storage.googleapis.com/mediapipe-models/"
MODELOS = {
    "dedos": ("hand_landmarker.task", _BASE + "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"),
    "rostos": ("face_detector.tflite", _BASE + "face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"),
    "objetos": ("efficientdet_lite0.tflite", _BASE + "object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite"),
}

CONEXOES_MAO = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]

TRADUCAO = {  # rótulos COCO mais comuns -> português
    "person": "pessoa", "cell phone": "celular", "cup": "copo", "bottle": "garrafa", "laptop": "notebook",
    "keyboard": "teclado", "mouse": "mouse", "book": "livro", "chair": "cadeira", "tv": "televisão",
    "couch": "sofá", "bed": "cama", "cat": "gato", "dog": "cachorro", "clock": "relógio", "scissors": "tesoura",
    "backpack": "mochila", "remote": "controle remoto", "bowl": "tigela", "apple": "maçã", "banana": "banana",
    "potted plant": "planta", "dining table": "mesa", "car": "carro", "bicycle": "bicicleta",
}


def contar_dedos(pts) -> int:
    """Conta dedos estendidos a partir de 21 pontos (x, y) de uma mão, em qualquer orientação."""
    d = lambda a, b: hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
    total = sum(1 for ponta, junta in ((8, 6), (12, 10), (16, 14), (20, 18)) if d(ponta, 0) > d(junta, 0) * 1.05)
    if d(4, 0) > d(9, 0) * 1.15:  # polegar: a ponta fica além do comprimento da palma
        total += 1
    return total


def plural(n: int, singular: str, plural_: str | None = None) -> str:
    return f"{n} {singular if n == 1 else (plural_ or singular + 's')}"


def baixar_modelo(modo: str) -> str:
    nome, url = MODELOS[modo]
    destino = PASTA_MODELOS / nome
    if not destino.exists():
        PASTA_MODELOS.mkdir(exist_ok=True)
        tmp = destino.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(destino)
    return str(destino)


class Camera:
    MODOS = ("movimento", "dedos", "rostos", "objetos")

    def __init__(self, falar, pasta="capturas", area_minima=1500, indice_camera=0):
        self.falar = falar
        self.pasta = Path(pasta)
        self.area_minima = area_minima
        self.indice = indice_camera
        self.cap = None
        self.modo = None
        self.sub = None
        self.detector = None
        self.ultimo_registro = 0.0
        self.historico = deque(maxlen=8)  # suaviza a contagem (evita "piscar")
        self.itens = []  # rótulos detectados no último frame (modo objetos)

    @property
    def ativa(self) -> bool:
        return self.cap is not None

    # ---------- ciclo de vida ----------
    def iniciar(self, modo="movimento"):
        if self.ativa and self.modo == modo:
            self.falar("A câmera já está nesse modo.")
            return
        if not self.ativa:
            backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
            cap = cv2.VideoCapture(self.indice, backend)
            if not cap.isOpened():
                self.falar("Não consegui acessar a câmera.")
                return
            self.cap = cap
        if not self._preparar(modo):
            if self.modo is None:
                self._liberar()
            return
        self.falar({
            "movimento": "Câmera ativada. Detectando movimentos.",
            "dedos": "Contando dedos. Mostre a mão para a câmera.",
            "rostos": "Contando rostos.",
            "objetos": "Contando objetos.",
        }[modo])

    def _preparar(self, modo) -> bool:
        novo = None
        if modo == "movimento":
            self.sub = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40, detectShadows=False)
            self.pasta.mkdir(exist_ok=True)
        else:
            try:
                if not (PASTA_MODELOS / MODELOS[modo][0]).exists():
                    self.falar("Baixando o modelo de inteligência artificial, só na primeira vez.")
                novo = self._criar_detector(modo, baixar_modelo(modo))
            except ImportError:
                self.falar("Falta instalar o MediaPipe. Rode: pip install mediapipe")
                return False
            except Exception as e:  # sem internet, arquivo corrompido etc.
                print(f"[erro modelo] {e}")
                self.falar("Não consegui carregar o modelo. Verifique a internet.")
                return False
        self.detector, self.modo = novo, modo
        self.historico.clear()
        self.itens = []
        return True

    @staticmethod
    def _criar_detector(modo, caminho):
        import mediapipe as mp
        from mediapipe.tasks import python as mpp
        from mediapipe.tasks.python import vision

        base = mpp.BaseOptions(model_asset_path=caminho)
        if modo == "dedos":
            return vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(base_options=base, num_hands=2))
        if modo == "rostos":
            return vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=base))
        return vision.ObjectDetector.create_from_options(
            vision.ObjectDetectorOptions(base_options=base, max_results=15, score_threshold=0.4)
        )

    def parar(self):
        if not self.ativa:
            self.falar("A câmera não está ativa.")
            return
        self._liberar()
        self.falar("Câmera desativada.")

    def _liberar(self):
        if self.cap:
            self.cap.release()
        self.cap = self.modo = self.detector = None
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    # ---------- resposta por voz ----------
    def contagem_estavel(self):
        return Counter(self.historico).most_common(1)[0][0] if self.historico else None

    def responder(self, filtro=None):
        """Fala o que está vendo agora, conforme o modo."""
        if not self.ativa or self.modo == "movimento":
            self.falar("Nenhuma contagem ativa.")
        elif self.modo == "objetos":
            itens = [TRADUCAO.get(i, i) for i in self.itens]
            if filtro:
                self.falar(f"Vejo {plural(itens.count(filtro), filtro, 'pessoas' if filtro == 'pessoa' else None)}.")
            elif not itens:
                self.falar("Não estou vendo nenhum objeto conhecido.")
            else:
                partes = [plural(n, nome, "pessoas" if nome == "pessoa" else None) for nome, n in Counter(itens).items()]
                self.falar("Vejo " + ", ".join(partes) + ".")
        else:
            n = self.contagem_estavel()
            if n is None:
                self.falar("Ainda não estou vendo nada.")
            elif self.modo == "dedos":
                self.falar(f"Vejo {plural(n, 'dedo')}." if n else "Não estou vendo dedos.")
            else:
                self.falar(f"Vejo {plural(n, 'rosto')}." if n else "Não estou vendo rostos.")

    # ---------- processamento de frames ----------
    def passo(self):
        """Processa um frame. Chame em loop enquanto `ativa`."""
        ok, frame = self.cap.read()
        if not ok:
            self._liberar()
            self.falar("Perdi o sinal da câmera.")
            return
        {"movimento": self._movimento, "dedos": self._dedos, "rostos": self._rostos, "objetos": self._objetos}[
            self.modo
        ](frame)
        cv2.imshow(JANELA, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.parar()

    @staticmethod
    def _texto(frame, txt, y=30, cor=(0, 255, 255)):
        cv2.putText(frame, txt, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
        cv2.putText(frame, txt, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

    def _mp_imagem(self, frame):
        import mediapipe as mp

        return mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    def _movimento(self, frame):
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
            self._texto(frame, "MOVIMENTO", cor=(0, 0, 255))
            agora = time.time()
            if agora - self.ultimo_registro > 2:  # no máximo 1 foto a cada 2 s
                self.ultimo_registro = agora
                cv2.imwrite(str(self.pasta / f"mov_{time.strftime('%Y%m%d_%H%M%S')}.jpg"), frame)

    def _dedos(self, frame, resultado=None):
        h, w = frame.shape[:2]
        resultado = resultado or self.detector.detect(self._mp_imagem(frame))
        total = 0
        for mao in resultado.hand_landmarks:
            pts = [(p.x * w, p.y * h) for p in mao]
            total += contar_dedos(pts)
            for a, b in CONEXOES_MAO:
                cv2.line(frame, tuple(map(int, pts[a])), tuple(map(int, pts[b])), (0, 255, 0), 2)
            for p in pts:
                cv2.circle(frame, (int(p[0]), int(p[1])), 4, (0, 0, 255), -1)
        self.historico.append(total if resultado.hand_landmarks else 0)
        self._texto(frame, f"Dedos: {self.contagem_estavel()}", cor=(0, 255, 0))

    def _rostos(self, frame, resultado=None):
        resultado = resultado or self.detector.detect(self._mp_imagem(frame))
        for d in resultado.detections:
            b = d.bounding_box
            cv2.rectangle(frame, (b.origin_x, b.origin_y), (b.origin_x + b.width, b.origin_y + b.height), (255, 128, 0), 2)
        self.historico.append(len(resultado.detections))
        self._texto(frame, f"Rostos: {self.contagem_estavel()}", cor=(255, 128, 0))

    def _objetos(self, frame, resultado=None):
        resultado = resultado or self.detector.detect(self._mp_imagem(frame))
        self.itens = []
        for d in resultado.detections:
            nome = d.categories[0].category_name
            self.itens.append(nome)
            b = d.bounding_box
            cv2.rectangle(frame, (b.origin_x, b.origin_y), (b.origin_x + b.width, b.origin_y + b.height), (0, 200, 255), 2)
            cv2.putText(frame, TRADUCAO.get(nome, nome), (b.origin_x, max(b.origin_y - 6, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
        self._texto(frame, f"Objetos: {len(self.itens)}", cor=(0, 200, 255))
