from typing import List, Optional

from src.domain.models.offer import Offer
from src.domain.ports.offer_repository_port import OfferRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class GetAllOffersUseCase(BaseUseCase):
    """Use case for getting all offers."""

    def __init__(self, offer_repository: OfferRepositoryPort):
        self.offer_repository = offer_repository

    def execute(self, postId: Optional[str], ownerId: Optional[str]) -> List[Offer]:
        return self.offer_repository.get_all(postId, ownerId)
