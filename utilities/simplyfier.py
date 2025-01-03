# from https://github.com/daquexian/onnx-simplifier

import onnx
from onnxsim import simplify

# load your predefined ONNX model
model = onnx.load("./pollinators_ds_v6_480_yolov5s_hyps_v0.onnx")

# convert model
model_simp, check = simplify(model)

assert check, "Simplified ONNX model could not be validated"

# use model_simp as a standard ONNX model object
