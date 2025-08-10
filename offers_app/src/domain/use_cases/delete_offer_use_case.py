from src.domain.models.offer import Offer
from src.domain.ports.offer_repository_port import OfferRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class DeleteOfferUseCase(BaseUseCase):
    """Use case for deleting a offer."""

    def __init__(self, offer_repository: OfferRepositoryPort):
        self.offer_repository = offer_repository

    def execute(self, offer_id: int) -> Offer:
        return self.offer_repository.delete(offer_id)
