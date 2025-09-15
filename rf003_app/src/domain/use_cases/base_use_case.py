from abc import ABC, abstractmethod
import logging


class BaseUseCase(ABC):
    """Base use case class."""
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the use case."""
        pass