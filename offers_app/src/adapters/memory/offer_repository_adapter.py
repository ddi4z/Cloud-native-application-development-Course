from typing import Dict, List, Optional

from src.domain.models.offer import Offer, OfferSize
from src.domain.ports.offer_repository_port import OfferRepositoryPort
from src.errors import OfferNotFoundError, InvalidFieldInOfferError, PreconditionOfferFailedError

import uuid

class InMemoryOfferRepositoryAdapter(OfferRepositoryPort):
    """In memory implementation of OfferRepository."""

    memory_store: Dict[uuid.uuid4, Offer] = {}

    def sequence(self) -> uuid.uuid4:
        """Generate a new sequence number."""
        return uuid.uuid4()

    def create(self, offer: Offer) -> Offer:
        """Create a new offer."""
        if offer.postId is None \
            or offer.userId is None \
            or offer.description is None \
            or offer.size is None \
            or offer.fragile is None \
            or offer.offer is None:
            raise InvalidFieldInOfferError(
                "All offer fields must be provided and non-null"
            )
        
        try:
            uuid.UUID(offer.postId)
            uuid.UUID(offer.userId)
        except ValueError:
            raise InvalidFieldInOfferError(
                "postId and userId must be valid UUID strings"
            )
        
        if offer.offer < 0:
            raise PreconditionOfferFailedError("offer must be a non-negative integer")
    
        if offer.size not in [size.value for size in OfferSize]:
            raise PreconditionOfferFailedError(
                f"size must be one of {[size.value for size in OfferSize]}"
            )

        offer.id = self.sequence()
        self.memory_store[offer.id] = offer
        return offer

    def get_by_id(self, offer_id: str) -> Optional[Offer]:
        """Get offer by ID."""

        try:
            identifier = uuid.UUID(offer_id)
        except ValueError:
            raise InvalidFieldInOfferError("offer_id must be a valid UUID string")

        return self.memory_store.get(identifier)

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
