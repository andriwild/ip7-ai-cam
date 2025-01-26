from ultralytics import YOLO

# Load the YOLO11 model
#model = YOLO("./resources/ml_models/yolov8n.pt")

# Export the model to NCNN format
#model.export(format="ncnn")  # creates '/yolo11n_ncnn_model'

# Load the exported NCNN model
ncnn_model = YOLO("./resources/ml_models/yolov8n_pollinator_ep50_v1_ncnn_model")

# Run inference
results = ncnn_model("./resources/images/pollinator_1.jpg")
results[0].show()
