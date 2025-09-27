from src.adapters.postgres.credit_card_repository_adapter import PostgresCreditCardRepositoryAdapter

print("Iniciando importación del adapter SQS...")
from src.adapters.sqs.verification_publisher_adapter import SQSVerificationPublisherAdapter
print("Importación del adapter SQS completada.")

from src.domain.use_cases.create_credit_card_use_case import CreateCreditCardUseCase
from src.domain.use_cases.get_credit_cards_by_user_use_case import GetCreditCardsByUserUseCase
from src.domain.use_cases.get_credit_cards_count_use_case import GetCreditCardsCountUseCase
from src.domain.use_cases.reset_credit_cards_use_case import ResetCreditCardsUseCase
from src.domain.use_cases.update_credit_card_status_use_case import UpdateCreditCardStatusUseCase


repository = PostgresCreditCardRepositoryAdapter()
publisher = SQSVerificationPublisherAdapter()


# Constructores de Casos de Uso 
def build_create_credit_card_use_case() -> CreateCreditCardUseCase:
    return CreateCreditCardUseCase(repository, publisher)

def build_get_credit_cards_by_user_use_case() -> GetCreditCardsByUserUseCase:
    return GetCreditCardsByUserUseCase(repository)

def build_get_credit_cards_count_use_case() -> GetCreditCardsCountUseCase:
    return GetCreditCardsCountUseCase(repository)

def build_reset_credit_cards_use_case() -> ResetCreditCardsUseCase:
    return ResetCreditCardsUseCase(repository)

def build_update_credit_card_status_use_case() -> UpdateCreditCardStatusUseCase:
    return UpdateCreditCardStatusUseCase(repository)
