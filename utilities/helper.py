import importlib  # To import modules dynamically at runtime

def is_library_available(library_name):
    """
    Check if a specific Python library is installed.

    This function attempts to import the library with the given name.
    If the import is successful, the library is available and it returns True.
    If not, an ImportError is caught and the function returns False.
    
    Parameters:
    - library_name (str): The name of the library to check.
    
    Returns:
    - bool: True if the library is installed, False otherwise.
    """
    try:
        importlib.import_module(library_name)
        return True
    except ImportError:
        return False


def load_labels(path: str):
    classes=[]
    file= open(path,'r')

    while True:
        name=file.readline().strip('\n')
        classes.append(name)
        if not name:
            break
    return classes
