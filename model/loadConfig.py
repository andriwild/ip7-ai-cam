class LoadConfig:
    """Represents an entity loaded from the YAML file."""
    def __init__(self, name, file_path=None, class_name=None, input_id=None, output_id=None, task=None, parameters=None):
        self.name = name
        self.file_path = file_path
        self.class_name = class_name
        self.input_id = input_id
        self.output_id = output_id
        self.task = task
        self.parameters = parameters

    def __repr__(self):
        return f"LoadDefinition(name={self.name}, file_path={self.file_path}, class_name={self.class_name})"
