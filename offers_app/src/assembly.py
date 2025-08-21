from src.adapters.memory.offer_repository_adapter import InMemoryOfferRepositoryAdapter

from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_offer_use_case import CreateOfferUseCase
from src.domain.use_cases.delete_offer_use_case import DeleteOfferUseCase
from src.domain.use_cases.get_offer_use_case import GetOfferUseCase
from src.domain.use_cases.get_offers_use_case import GetAllOffersUseCase
from src.domain.use_cases.update_offer_use_case import UpdateOfferUseCase
from src.domain.use_cases.count_offers_use_case import CountOffersUseCase
from src.domain.use_cases.reset_offers_use_case import ResetOffersUseCase

repository: InMemoryOfferRepositoryAdapter = InMemoryOfferRepositoryAdapter()


def build_create_offer_use_case() -> BaseUseCase:
    """Get create offer use case."""
    return CreateOfferUseCase(repository)


def build_get_offer_use_case() -> BaseUseCase:
    """Get offer use case."""
    return GetOfferUseCase(repository)


def build_get_offers_use_case() -> BaseUseCase:
    """Get offers use case."""
    return GetAllOffersUseCase(repository)


def build_update_offer_use_case() -> BaseUseCase:
    """Update offer use case."""
    return UpdateOfferUseCase(repository)


def build_delete_offer_use_case() -> BaseUseCase:
    """Get delete offer use case."""
    return DeleteOfferUseCase(repository)

def build_count_offers_use_case() -> BaseUseCase:
    """Get the numbers of offers use case."""
    return CountOffersUseCase(repository)

def build_reset_offers_use_case() -> BaseUseCase:
    """Get reset offers use case."""
    return ResetOffersUseCase(repository)
