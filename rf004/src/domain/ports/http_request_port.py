from abc import ABC, abstractmethod

class HttpRequestPort(ABC):
    @abstractmethod
    def ping() -> bool:
        raise NotImplementedError("This method should be overridden in subclasses")