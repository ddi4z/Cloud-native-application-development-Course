import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.models.offer import Offer, OfferSize
from src.domain.ports.offer_repository_port import OfferRepositoryPort
from src.errors import (
    InvalidFieldInOfferError,
    OfferNotFoundError,
    PreconditionOfferFailedError,
)

from .models import OfferORM


class PostgresOfferRepositoryAdapter(OfferRepositoryPort):
    def __init__(self, session_factory=Session):
        self._session_factory = session_factory

    def create(self, offer: Offer) -> Offer:
        """Create a new offer."""
        if (
            offer.postId is None
            or offer.userId is None
            or offer.description is None
            or offer.size is None
            or offer.fragile is None
            or offer.offer is None
        ):
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
        with self._session_factory() as db_session:
            orm = OfferORM.from_domain(offer)
            db_session.add(orm)
            db_session.commit()
            db_session.refresh(orm)
            return orm.to_domain()

    def get_by_id(self, offer_id: str) -> Optional[Offer]:
        """Get offer by ID."""

        try:
            identifier = uuid.UUID(offer_id)
        except ValueError:
            raise InvalidFieldInOfferError("offer_id must be a valid UUID string")

        with self._session_factory() as db_session:
            orm = db_session.query(OfferORM).filter(OfferORM.id == identifier).first()
            if orm is None:
                raise OfferNotFoundError(f"offer with id {offer_id} not found")
            return orm.to_domain()

    def get_all(self, postId: Optional[str], ownerId: Optional[str]) -> list[Offer]:
        with self._session_factory() as db_session:
            offers: List[OfferORM] = db_session.query(OfferORM).all()
            mapped_offers: List[Offer] = list(map(lambda x: x.to_domain(), offers))
            if postId is None and ownerId is None:
                return mapped_offers

            try:
                uuid.UUID(postId) if postId is not None else None
                uuid.UUID(ownerId) if ownerId is not None else None
            except ValueError:
                raise InvalidFieldInOfferError(
                    "postId and ownerId must be valid UUID strings"
                )

            # only filter by postId
            filtered_by_postId: List[Offer] = [
                offer for offer in mapped_offers if offer.postId == postId
            ]
            if postId is not None and ownerId is None:
                return filtered_by_postId

            filtered_by_ownerId: List[Offer] = [
                offer for offer in mapped_offers if offer.userId == ownerId
            ]
            if ownerId is not None and postId is None:
                return filtered_by_ownerId

            # filter by both postId and ownerId
            return [
                offer
                for offer in mapped_offers
                if offer.postId == postId and offer.userId == ownerId
            ]

    def delete(self, offer_id: str) -> Offer:
        """Delete an offer."""
        try:
            identifier = uuid.UUID(offer_id)
        except ValueError:
            raise InvalidFieldInOfferError("offer_id must be a valid UUID string")

        with self._session_factory() as db_session:
            orm = db_session.query(OfferORM).filter(OfferORM.id == identifier).first()
            if orm is None:
                raise OfferNotFoundError(f"offer with id {offer_id} not found")
            db_session.delete(orm)
            db_session.commit()
            return orm.to_domain()

    def reset(self) -> None:
        """Reset the offers repository."""
        with self._session_factory() as db_session:
            db_session.query(OfferORM).delete()
            db_session.commit()

    def count(self) -> int:
        """Count the number of offers."""
        with self._session_factory() as db_session:
            return db_session.query(OfferORM).count()
