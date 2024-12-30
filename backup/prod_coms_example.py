import time
import threading
import queue
from abc import ABC, abstractmethod
import numpy as np

########################
# Frame Provider Interface and Implementations (Adapter-like pattern)
########################

class FrameProvider(ABC):
    @abstractmethod
    def get_frame(self):
        """Return a frame. Could be a numpy array, an image, etc."""
        pass

class CameraFrameProvider(FrameProvider):
    def __init__(self, camera_id=0):
        # In a real implementation, you would open a camera source, e.g. cv2.VideoCapture
        # Here, we simulate with a random matrix as a frame.
        self.camera_id = camera_id

    def get_frame(self):
        # Simulate retrieving a frame from a camera
        # Replace with actual cv2.VideoCapture logic in a real scenario
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

class StaticImageFrameProvider(FrameProvider):
    def __init__(self, image_path):
        # In a real implementation, load the image once (e.g., via cv2.imread)
        # Here we simulate a static image as a random matrix
        self.static_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def get_frame(self):
        # Always returns the same static frame
        return self.static_frame

class InMemoryMatrixFrameProvider(FrameProvider):
    def __init__(self, matrix):
        # matrix should be a numpy array representing a frame
        self.matrix = matrix

    def get_frame(self):
        return self.matrix

########################
# Inference Strategy Interface and Implementations
########################

class InferenceStrategy(ABC):
    @abstractmethod
    def inference(self, frame):
        """Run inference on the given frame and return annotated results."""
        pass

class UltralyticsInferenceStrategy(InferenceStrategy):
    def __init__(self):
        # In a real implementation, load a model from ultralytics
        # Example: from ultralytics import YOLO; self.model = YOLO('yolov8n.pt')
        pass

    def inference(self, frame):
        # Simulate inference (in real code, run model prediction here)
        # E.g.:
        # results = self.model(frame)
        # annotated_frame = results.plot()
        # return annotated_frame
        # For now, simulate annotation by adding a random bounding box:
        annotated_frame = frame.copy()
        # pretend we drew a box or wrote text
        return annotated_frame

class SimulatedInferenceStrategy(InferenceStrategy):
    def inference(self, frame):
        # Just pretend we do something to the frame, e.g. add a text overlay
        annotated_frame = frame.copy()
        # No actual drawing code, just return the same frame
        return annotated_frame

########################
# Producer-Consumer Setup
########################

class FrameProducer:
    def __init__(self, frame_provider: FrameProvider, frame_queue: queue.Queue):
        self.frame_provider = frame_provider
        self.frame_queue = frame_queue
        self.stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while not self.stop_event.is_set():
            frame = self.frame_provider.get_frame()
            self.frame_queue.put(frame)
            time.sleep(0.05)  # Simulate a frame rate

    def stop(self):
        self.stop_event.set()

class FrameConsumer:
    def __init__(self, frame_queue: queue.Queue, inference_strategy: InferenceStrategy):
        self.frame_queue = frame_queue
        self.inference_strategy = inference_strategy
        self.stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while not self.stop_event.is_set():
            try:
                frame = self.frame_queue.get(timeout=1.0)
                annotated = self.inference_strategy.inference(frame)
                # Here we would do something with the annotated frame:
                # e.g., display, send over a stream, store in DB.
                # For demonstration, we just print a message:
                print("Consumed and annotated a frame:", annotated.shape)
                self.frame_queue.task_done()
            except queue.Empty:
                pass

    def stop(self):
        self.stop_event.set()

########################
# Example Usage
########################

if __name__ == "__main__":
    # Create a queue to hold frames
    q = queue.Queue(maxsize=10)

    # Choose a frame provider
    # For example, replace with CameraFrameProvider or StaticImageFrameProvider as needed.
    # Example 1: Camera frame provider
    camera_provider = CameraFrameProvider()

    # Example 2: Static image provider
    # static_provider = StaticImageFrameProvider("dummy_path")

    # Example 3: In memory matrix
    # test_matrix = np.zeros((480, 640, 3), dtype=np.uint8)
    # in_memory_provider = InMemoryMatrixFrameProvider(test_matrix)

    # Choose an inference strategy
    # Real inference
    real_inference = UltralyticsInferenceStrategy()
    # Simulated inference
    simulated_inference = SimulatedInferenceStrategy()

    # Setup producer and consumer with chosen provider and strategy
    producer = FrameProducer(frame_provider=camera_provider, frame_queue=q)
    consumer = FrameConsumer(frame_queue=q, inference_strategy=simulated_inference)

    producer.start()
    consumer.start()

    # Run for a bit and then stop
    time.sleep(2)
    producer.stop()
    consumer.stop()
