import importlib.util
import os
import logging

logger = logging.getLogger(__name__)

class ClassLoader:

    _class_cache = {}

    @staticmethod
    def from_path(file_path, class_name):
        """Dynamically load a class from a specified file."""
        try:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            # Check if the class is already loaded and cached
            if (file_path, class_name) in ClassLoader._class_cache:
                return ClassLoader._class_cache[(file_path, class_name)]

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded_class = getattr(module, class_name)
            
            # Cache the loaded class
            ClassLoader._class_cache[(file_path, class_name)] = loaded_class
            return loaded_class
        except (ImportError, AttributeError, FileNotFoundError) as e:
            logger.error(f"Error loading class '{class_name}' from file '{file_path}': {e}")
            return None



    @staticmethod
    def instantiate_class(load_config):
        file_path  = load_config.get("file_path")
        class_name = load_config.get("class_name")
        name       = load_config.get("name")
        params     = load_config.get("parameters", {})

        assert file_path and class_name and name

        src_cls = ClassLoader.from_path(file_path, class_name)
        if not src_cls:
            logger.error(f"Failed to load class {class_name} from {file_path}")
            exit(1)

        return src_cls(name, params)


    # def get_source_config_by_name(self, name: str):
    #     sources = [LoadConfig(**source) for source in self._config["sources"]]
    #     for source in sources:
    #         if source.name == name:
    #             return source
    #     return None


    # def get_sink_config_by_name(self, name: str):
    #     sinks = [LoadConfig(**sink) for sink in self._config["sinks"]]
    #     for sink in sinks:
    #         if sink.name == name:
    #             return sink
    #     return None


    # def get_step_config_by_name(self, name: str):
    #     steps = [LoadConfig(**step) for step in self._config["steps"]]
    #     for step in steps:
    #         if step.name == name:
    #             return step
    #     return None
