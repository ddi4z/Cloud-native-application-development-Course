from abc import ABC, abstractmethod

class HttpRequest(ABC):
    """Offer repository interface."""

    @abstractmethod
    def ping(self) -> bool:
        """Create a new offer."""
        raise NotImplementedError("This method should be overridden in subclasses")
