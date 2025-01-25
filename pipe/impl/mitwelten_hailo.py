from pipe.base.operation import Operation
from picamera2.devices import Hailo
from model.detection import Detection, Box
from model.model import Frame
from pipe.impl.hailoDetect import HailoObjectDetection
from utilities.labelLoader import load_labels
import logging

logger = logging.getLogger(__name__)

class Mitwelten(Operation):
    def __init__(self, name: str, params = {}):
        logger.info(f"Initializing Mitwelten inference with name {name}")
        super().__init__(name)

        pollinator_params     = params.get("pollinator_params", {})
        pollinator_model      = pollinator_params.get("pollinator_model", "./resources/ml_models/yolov8n_pollinator_ep50_v1.hef")
        pollinator_label_path = pollinator_params.get("label_path")
        self.pollinator_batch_size = pollinator_params.get("batch_size", 4)

        self.conf_threshold = pollinator_params.get('confidence_threshold', 0.5)
        self.input_size = (640, 640)
        self._pollinator_labels = load_labels(pollinator_label_path)

        self.flower_hailo_model     = HailoObjectDetection('flower_inference', params.get("flower_params", {}))
        self.pollinator_hailo_model = Hailo(pollinator_model, batch_size=self.pollinator_batch_size)
        logger.info(f"Initialized Mitwelten inference with name {name}")
        

    def process(self, frame: Frame) -> list[Detection]:
        # Erste Inferenz (Blumenerkennung)
        result_boxes: list[Box] = []
        flower_detections: list[Box] = self.flower_hailo_model.process(frame)
        result_boxes.extend(flower_detections)

        # Originale Bilddimensionen
        orig_height, orig_width = frame.image.shape[:2]

        # Vorbereitung für Pollinator-Inferenz
        cropped_flowers = []
        letterbox_data = []

        for flower_detection in flower_detections:
            fh = flower_detection.xywhn[3]
            fw = flower_detection.xywhn[2]
            fy = flower_detection.xywhn[1]
            fx = flower_detection.xywhn[0]

            x1 = int((fx - fw/2) * orig_width)
            y1 = int((fy - fh/2) * orig_height)
            x2 = int((fx + fw/2) * orig_width)
            y2 = int((fy + fh/2) * orig_height)

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(orig_width, x2), min(orig_height, y2)

            cropped_image = frame.image[y1:y2, x1:x2]

            # Letterbox vorbereiten (oder falls Hailo das selbst macht, entsprechende Werte abrufen)
            resized_h, resized_w = self.input_size
            h0, w0 = cropped_image.shape[:2]
            r = min(resized_w / w0, resized_h / h0) if (w0 > 0 and h0 > 0) else 1.0
            nw, nh = int(w0 * r), int(h0 * r)
            pad_left = (resized_w - nw) // 2
            pad_top  = (resized_h - nh) // 2

            letterboxed_img = np.full((resized_h, resized_w, 3), 114, dtype=np.uint8)
            resized = cv2.resize(cropped_image, (nw, nh), interpolation=cv2.INTER_LINEAR)
            letterboxed_img[pad_top:pad_top+nh, pad_left:pad_left+nw] = resized

            tmp_frame = Frame(
                image=letterboxed_img,
                timestamp=frame.timestamp,
                frame_id=frame.frame_id,
                source_id=frame.source_id
            )
            cropped_flowers.append(tmp_frame)

            letterbox_data.append({
                'ratio': r,
                'pad_left': pad_left,
                'pad_top': pad_top,
                'orig_x1': x1,
                'orig_y1': y1,
                'orig_w': orig_width,
                'orig_h': orig_height
            })

        # Zweite Inferenz (Bestäubererkennung) - nur batch_size Bilder pro run()
        result = []
        for i in range(0, len(cropped_flowers), self.pollinator_batch_size):
            # Chunk bilden
            sub_batch_frames = cropped_flowers[i : i + self.pollinator_batch_size]
            sub_batch_letterbox_data = letterbox_data[i : i + self.pollinator_batch_size]

            # Inferenz ausführen
            inference_results = self.pollinator_hailo_model.run(sub_batch_frames)

            # Ergebnisse zurückprojizieren
            for j, inference in enumerate(inference_results):
                data     = sub_batch_letterbox_data[j]
                ratio    = data['ratio']
                pad_left = data['pad_left']
                pad_top  = data['pad_top']
                offset_x = data['orig_x1']
                offset_y = data['orig_y1']
                w_img    = data['orig_w']
                h_img    = data['orig_h']

                for idx, class_detections in enumerate(inference):
                    for detection in class_detections:
                        if len(detection) >= 5:
                            conf = detection[4]
                            if conf > self.conf_threshold:
                                # yxyx (normalisiert)
                                y1_norm, x1_norm, y2_norm, x2_norm = detection[:4]

                                # Auf Letterboxgröße zurückrechnen
                                x1_l = x1_norm * self.input_size[0]
                                x2_l = x2_norm * self.input_size[0]
                                y1_l = y1_norm * self.input_size[1]
                                y2_l = y2_norm * self.input_size[1]

                                # Padding entfernen & zurückskalieren
                                x1_un = (x1_l - pad_left) / ratio
                                x2_un = (x2_l - pad_left) / ratio
                                y1_un = (y1_l - pad_top)  / ratio
                                y2_un = (y2_l - pad_top)  / ratio

                                # Offset für originale Koordinaten
                                x1_final = x1_un + offset_x
                                x2_final = x2_un + offset_x
                                y1_final = y1_un + offset_y
                                y2_final = y2_un + offset_y

                                # In xywhn
                                x_center = (x1_final + x2_final) / 2
                                y_center = (y1_final + y2_final) / 2
                                w = x2_final - x1_final
                                h = y2_final - y1_final

                                result.append(
                                    Box(
                                        xywhn=(
                                            x_center / w_img,
                                            y_center / h_img,
                                            w / w_img,
                                            h / h_img
                                        ),
                                        conf=conf,
                                        label=self._pollinator_labels[idx]
                                    )
                                )

        # Gesamtergebnis zurückgeben
        result_boxes.extend(result)
        return result_boxes       
