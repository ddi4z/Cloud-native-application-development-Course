from typing import Dict, List, Optional

from src.domain.models.offer import Offer, OfferSize
from src.domain.ports.offer_repository_port import OfferRepositoryPort
from src.errors import OfferNotFoundError, InvalidFieldInOfferError, PreconditionOfferFailedError

import uuid

class PostgresOfferRepositoryAdapter(OfferRepositoryPort):
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
        
        if identifier not in self.memory_store:
            raise OfferNotFoundError(f"offer with id {offer_id} not found")

        return self.memory_store.get(identifier)


    def get_all(self, postId: Optional[str], ownerId: Optional[str]) -> List[Offer]:
        """Get all offers."""
        if postId is None and ownerId is None:
            return list(self.memory_store.values())
        print(postId, ownerId)
        postId_uuid, ownerId_uuid = None, None
        try:
            postId_uuid = uuid.UUID(postId) if postId is not None else None
            ownerId_uuid = uuid.UUID(ownerId) if ownerId is not None else None
        except ValueError:
            raise InvalidFieldInOfferError("postId and ownerId must be valid UUID strings")

        filtered_by_posts = [
            offer for offer in self.memory_store.values()
            if postId is not None and uuid.UUID(offer.postId) == postId_uuid
        ]
        if postId is not None and ownerId is None:
            return list(filtered_by_posts)
        
        filtered_by_owners = [
            offer for offer in self.memory_store.values()
            if ownerId is not None and uuid.UUID(offer.userId) == ownerId_uuid
        ]
        if ownerId is not None and postId is None:
            return list(filtered_by_owners)

        return [
            offer for offer in self.memory_store.values()
            if (postId is None or uuid.UUID(offer.postId) == postId_uuid) and
               (ownerId is None or uuid.UUID(offer.userId) == ownerId_uuid)
        ]

    def delete(self, offer_id: str) -> Offer:
        """Delete an offer."""
        try:
            identifier = uuid.UUID(offer_id)
        except ValueError:
            raise InvalidFieldInOfferError("offer_id must be a valid UUID string")

        if identifier not in self.memory_store:
            raise OfferNotFoundError(f"offer with id {offer_id} not found")

        offer = self.memory_store[identifier]
        del self.memory_store[identifier]
        return offer
    
    def count(self) -> int:
        """Count the number of offers."""
        return len(self.memory_store)
    
    def reset(self) -> None:
        """Reset the offers repository."""
        self.memory_store.clear()
