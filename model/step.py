from dataclasses import dataclass


@dataclass
class Step:
    def __init__(self, name, class_name, file_path, input, output, parameters=None):
        self.name = name
        self.class_name = class_name
        self.file_path = file_path
        self.input = input
        self.output = output
        self.parameters = parameters or {}

