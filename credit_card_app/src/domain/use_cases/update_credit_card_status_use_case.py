from uuid import UUID
from typing import Optional
from src.domain.models.credit_card import CreditCard, CreditCardStatus
from src.domain.ports.credit_card_repository_port import CreditCardRepositoryPort

class UpdateCreditCardStatusUseCase:
    def __init__(self, repository: CreditCardRepositoryPort):
        self.repository = repository
        
    def execute(self, card_id: UUID, status: CreditCardStatus) -> Optional[CreditCard]:
        return self.repository.update_status(card_id, status)