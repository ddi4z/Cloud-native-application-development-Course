from src.domain.ports.credit_card_repository_port import CreditCardRepositoryPort

class ResetCreditCardsUseCase:
    def __init__(self, repository: CreditCardRepositoryPort):
        self.repository = repository

    def execute(self) -> None:
        self.repository.reset()