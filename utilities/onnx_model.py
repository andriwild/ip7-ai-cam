from ultralytics import YOLO

# Load your pre-trained model
model = YOLO('yolo11n.pt')

# Export the model
model.export(format='onnx', 
            batch=1, 
            device='cpu', 
            simplify=True, 
            #imgsz=640, 
            dynamic=True)
