from typing import Dict, List, Optional

from src.domain.models.offer import Offer
from src.domain.ports.offer_repository_port import OfferRepositoryPort
from errors import OfferNotFoundError


class InMemoryOfferRepositoryAdapter(OfferRepositoryPort):
    """In memory implementation of OfferRepository."""

    memory_store: Dict[int, Offer] = {}

    def sequence(self) -> int:
        """Generate a new sequence number."""
        return len(self.memory_store) + 1

    # TODO: Implement
    def create(self, offer: Offer) -> Offer:
        """Create a new offer."""
        offer.id = self.sequence()
        self.memory_store[offer.id] = offer
        return offer

    def get_by_id(self, offer_id: int) -> Optional[Offer]:
        """Get offer by ID."""
        return self.memory_store.get(offer_id)

    def get_all(self) -> List[Offer]:
        """Get all offers."""
        return list(self.memory_store.values())

    def update(self, offer: Offer) -> Offer:
        """Update an existing offer."""
        if offer.id not in self.memory_store:
            raise OfferNotFoundError(f"offer with id {offer.id} not found")
        self.memory_store[offer.id] = offer
        return offer

    def delete(self, offer_id: int) -> Offer:
        """Delete an offer."""
        if offer_id not in self.memory_store:
            raise OfferNotFoundError(f"offer with id {offer_id} not found")
        offer = self.memory_store[offer_id]
        del self.memory_store[offer_id]
        return offer
