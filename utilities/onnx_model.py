from ultralytics import YOLO
import torch
MODEL_PATH = 'resources/ml_models/'


def ultralytics_export(model = 'yolo11n.pt'):
    model = YOLO(MODEL_PATH + model)
    
    # Export the model
    model.export(format='onnx', 
                batch=1, 
                device='cpu', 
                simplify=True, 
                #imgsz=640, 
                dynamic=False)
    
    #model.export(format='imx500', 
    #            batch=1, 
    #            device='cpu', 
    #            simplify=True, 
    #            #imgsz=640, 
    #            dynamic=True)
    
    # to ncnn: pip instal pnnx && pnnx models/flower_n_sim.onnx

def onnx_export(model = 'yolo11n.pt'):
    model = torch.load(MODEL_PATH + model)
    #model.eval()
    dummy_input = torch.randn(1, 3, 224, 224) 
    torch.onnx.export(
        model,
        dummy_input,
        "model.onnx",
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},   # Erlaubt variablen Batch im ONNX
            "output": {0: "batch_size"}   # Ggf. auch hier dynamisch
        },
        opset_version=11  # oder eine höhere Version, je nach Bedarf
    )


def imx500():
    
    # Load a YOLOv8n PyTorch model
    model = YOLO("yolov8n.pt")
    
    # Export the model
    model.export(format="imx")  # exports with PTQ quantization by default
    
    # Load the exported model
    imx_model = YOLO("yolov8n_imx_model")
    
    # Run inference
    results = imx_model("https://ultralytics.com/images/bus.jpg")
    results[0].plot()


if __name__ == '__main__':
    ultralytics_export("yolov8s_flower.pt")
    #onnx_export()
    #imx500()
    print("Done")
