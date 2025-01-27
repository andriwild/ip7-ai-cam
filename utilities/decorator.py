import logging
import time

def Log_time(name=None):
    """
    Logs the time of the method execution on log level DEBUG.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                elapsed_time = end_time - start_time
                log_name = name if name else func.__name__
                logging.debug(f"Execution time of '{log_name}' took {elapsed_time} ms")
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator
