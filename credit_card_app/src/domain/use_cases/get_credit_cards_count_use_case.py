from src.domain.ports.credit_card_repository_port import CreditCardRepositoryPort

class GetCreditCardsCountUseCase:
    def __init__(self, repository: CreditCardRepositoryPort):
        self.repository = repository

    def execute(self) -> int:
        return self.repository.count()