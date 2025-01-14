from collections import defaultdict
import importlib.util
from typing import Any
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
    def instances_from_config(loaded_config):
        logger.info("Load classes from config ...")
        # top level configuration names (e.g. source, pipe, sink)
        categories: list[str] = loaded_config.keys()
    
        # mapping: name -> instance of the corresponding class
        instances: dict[str, Any] = defaultdict(dict)
    
        for category in categories:
            all_class_configs = loaded_config.get(category, [])
    
            for class_config in all_class_configs:
                file_path    = class_config.get("file_path")
                class_name   = class_config.get("class_name")
                loaded_class = ClassLoader.from_path(file_path, class_name)
    
                if loaded_class is not None:
                    name   = class_config.get("name")
                    params = class_config.get("parameters", {})
                    instance = loaded_class(name, params)
                    instances[category][class_config["name"]] = instance
    
        logger.info(f"Loaded {len(instances.keys())} classes from config")
        return instances

