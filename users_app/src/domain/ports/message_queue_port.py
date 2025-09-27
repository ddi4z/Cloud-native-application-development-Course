from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models.user import User


class MessageQueuePort(ABC):
    """Message queue port interface."""

    @abstractmethod
    def send_message(self, message: dict) -> None:
        """Send a message to the message queue."""
        raise NotImplementedError("This method should be overridden by subclasses.")
