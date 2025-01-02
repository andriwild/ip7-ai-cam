import importlib.util
import os

class ClassLoader:

    _class_cache = {}

    @staticmethod
    def get_class_from_file(file_path, class_name):
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
            print(f"Error loading class '{class_name}' from file '{file_path}': {e}")
            return None
