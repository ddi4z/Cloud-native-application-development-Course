from abc import ABC, abstractmethod
from uuid import UUID

class VerificationPublisherPort(ABC):
    @abstractmethod
    def publish_for_polling(self, card_id: UUID, ruv: str, user_email: str) -> None:
        pass