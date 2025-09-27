from functools import wraps

from requests.exceptions import RequestException

from src.errors import UnavailableService


def catch_unavailable_service(service_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (RequestException, ConnectionError, TimeoutError) as _:
                raise UnavailableService(f"{service_name} service is not available")

        return wrapper

    return decorator
