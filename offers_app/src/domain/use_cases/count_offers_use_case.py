from src.domain.ports.offer_repository_port import OfferRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class CountOffersUseCase(BaseUseCase):
    """Use case for count the number of offers in the database."""

    def __init__(self, offer_repository: OfferRepositoryPort):
        self.offer_repository = offer_repository

    def execute(self) -> int:
        """Create a new offer."""
        return self.offer_repository.count()
