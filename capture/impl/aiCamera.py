import time
import logging
from datetime import datetime

import cv2
import numpy as np

from capture.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)

class Detection:
    """
    Repräsentiert einen einzelnen Detektions-Output
    """
    def __init__(self, box, category, conf):
        self.box = box         # (x, y, width, height)
        self.category = category
        self.conf = conf

class AiCamera(Source):

    NAME = "ai"

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        model_path: str = "/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk",
        threshold: float = 0.5,
        iou: float = 0.5
    ):
        """
        :param width: Breite des auszugebenden Frames.
        :param height: Höhe des auszugebenden Frames.
        :param model_path: Pfad zum RPK-Modell für die IMX500.
        :param threshold: Konfidenz-Schwelle für die Detektionen.
        :param iou: IOU-Schwelle (falls Post-Processing sie braucht).
        """
        logger.info("Initializing AiCamera")

        from picamera2 import Picamera2
        from picamera2.devices import IMX500, NetworkIntrinsics
        from picamera2.devices.imx500 import postprocess_nanodet_detection

        # --- Merke dir verlinkte Klassen für später (Postprocessing) ---
        self._IMX500 = IMX500
        self._postprocess_nanodet_detection = postprocess_nanodet_detection
        self._NetworkIntrinsics = NetworkIntrinsics

        # --- Netzwerkspezifische Variablen ---
        self._model_path = model_path
        self._threshold = threshold
        self._iou = iou

        # IMX500 initialisieren (lädt das Modell)
        self._imx500 = self._IMX500(self._model_path)
        self._intrinsics = self._imx500.network_intrinsics
        if not self._intrinsics:
            # Falls das Modell keine Intrinsics definiert hat, legen wir ein Default-Objekt an
            self._intrinsics = self._NetworkIntrinsics()
            self._intrinsics.task = "object detection"

        # Picamera2 mit dem IMX500-Kameramodul
        self._camera = Picamera2(self._imx500.camera_num)

        # Eine Preview-Konfiguration erstellen, die das gewünschte Format/die gewünschte Größe liefert
        config = self._camera.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"},
            buffer_count=4,  # Je nach Bedarf mehr Buffer
            controls={"FrameRate": self._intrinsics.inference_rate if self._intrinsics.inference_rate else 10}
        )

        # Kamera starten
        self._camera.start(config)
        time.sleep(1)  # kurze Wartezeit, damit die Kamera stabil läuft

        logger.info("AiCamera initialization complete.")

    def get_frame(self) -> Frame:
        """
        Liest das aktuelle Kamerabild als numpy-Array aus, führt eine Inferenz durch (über Metadata),
        zeichnet ggf. gefundene Bounding Boxen ins Bild und gibt ein Frame-Objekt zurück.
        """
        logger.debug("Getting frame from AiCamera")

        # 1) Metadata aus dem Inferenz-Pfad abfragen
        metadata = self._camera.capture_metadata()

        # 2) parse_detections aufrufen: erhalte Liste von Detection-Objekten
        detections = self._parse_detections(metadata)

        # 3) Nun das eigentliche Farbbild (RGB888) abgreifen
        frame_data = self._camera.capture_array("main")

        # 4) Bounding Boxen (und Labels) auf das numpy-Array malen
        frame_data_annotated = self._draw_detections(frame_data, detections)

        # 5) Frame-Objekt erstellen und zurückgeben
        timestamp = datetime.now()
        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame_data_annotated,
            timestamp=timestamp
        )

    def _parse_detections(self, metadata: dict):
        """
        Übersetzt die Inferenz-Ausgabe des IMX500 in eine Liste von Detection-Objekten.
        Hier ein vereinfachter Ansatz für generische Box-Outputs [N, 4], Scores [N], ClassIDs [N].
        Falls du Nanodet-Postprocessing o.Ä. benötigst, musst du mehr Logik implementieren.
        """
        if metadata is None:
            return []

        # Aus den Metadata die Inferenz-Outputs abgreifen
        np_outputs = self._imx500.get_outputs(metadata, add_batch=True)
        if np_outputs is None:
            return []

        # Normalerweise: [0] -> Boxes, [1] -> Scores, [2] -> Classes
        # Sofern dein Modell das liefert. Ggfs. musst du anpassen.
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]

        # Filtere nach Konfidenz:
        valid_indices = np.where(scores >= self._threshold)[0]
        boxes   = boxes[valid_indices]
        scores  = scores[valid_indices]
        classes = classes[valid_indices]

        # Optional: Falls dein Modell bounding boxes normalisiert ausgibt
        # oder in xyxy / yxyx / xywh, etc. hast du hier Konvertierungen:
        # Beispiel: Wir nehmen an, Boxes sind yxxy normalisiert [y0, x0, y1, x1] ∈ [0..1].
        # Dann kann man das in Pixel-Koordinaten des ISP-Streams konvertieren:
        (img_h, img_w, _) = self._camera.stream_configuration("main")["size"][::-1]  # (height, width)
        # Wir unterstellen y0, x0, y1, x1 (0..1):
        # Ggfs. je nach "bbox_order" in intrinsics anpassen
        detections = []
        for (y0, x0, y1, x1), score, category in zip(boxes, scores, classes):
            # Auf Pixel skalieren
            top_left_y = int(y0 * img_h)
            top_left_x = int(x0 * img_w)
            br_y       = int(y1 * img_h)
            br_x       = int(x1 * img_w)

            width_box  = br_x - top_left_x
            height_box = br_y - top_left_y

            detections.append(
                Detection(
                    box=(top_left_x, top_left_y, width_box, height_box),
                    category=int(category),
                    conf=float(score)
                )
            )

        return detections

    def _draw_detections(self, frame_data: np.ndarray, detections: list) -> np.ndarray:
        """
        Zeichnet die im parse_detections erkannten Bounding Boxes und Labels ins gegebene frame_data.
        Gibt das bearbeitete (annotierte) Array zurück.
        """
        # In intrinsics könnten Label-Listen liegen (COCO, etc.)
        labels = self._intrinsics.labels or []
        overlay = frame_data.copy()

        for detection in detections:
            x, y, w, h = detection.box
            category_text = ""
            if detection.category < len(labels) and labels[detection.category]:
                category_text = labels[detection.category]
            else:
                category_text = f"ID {detection.category}"

            label = f"{category_text} ({detection.conf:.2f})"

            # Zeichne Bounding Box
            cv2.rectangle(
                overlay,
                (x, y),
                (x + w, y + h),
                color=(0, 255, 0),  # BGR: Grün
                thickness=2
            )
            # Text
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            text_x = x + 5
            text_y = max(y + 15, 15)  # minimaler Offset, damit man Text nicht "oben" verliert

            # Kleines halbtransparentes Feld hinter dem Text
            cv2.rectangle(
                overlay,
                (text_x, text_y - text_height),
                (text_x + text_width, text_y + baseline),
                (255, 255, 255),
                -1  # filled
            )
            alpha = 0.4
            cv2.addWeighted(overlay, alpha, frame_data, 1 - alpha, 0, frame_data)

            # Danach Text in frame_data malen
            cv2.putText(
                frame_data, label, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )

        return frame_data

    def release(self):
        """
        Gibt die Kamera-Ressourcen frei.
        """
        if self._camera is not None:
            logger.info("Releasing AiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None

    def get_name(self) -> str:
        logger.debug("Getting source name for AiCamera")
        return self.NAME
