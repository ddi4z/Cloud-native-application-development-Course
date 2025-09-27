from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.models.credit_card import CreditCard, CreditCardStatus

class CreditCardRepositoryPort(ABC):
    @abstractmethod
    def save(self, card: CreditCard) -> CreditCard:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[CreditCard]:
        pass

    @abstractmethod
    def update_status(self, card_id: UUID, status: CreditCardStatus) -> Optional[CreditCard]:
        pass

    @abstractmethod
    def find_by_last_four_digits(self, user_id: str, last_four: str) -> Optional[CreditCard]:
        pass
    
    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass