from src.domain.models.offer import Offer
from src.domain.ports.offer_repository_port import OfferRepositoryPort

from sqlalchemy.orm import Session
from .models import OfferORM
from src.domain.models.offer import OfferSize
from src.errors import (
    InvalidFieldInOfferError,
    PreconditionOfferFailedError
)
import uuid

class PostgresOfferRepositoryAdapter(OfferRepositoryPort):
    def __init__(self, session_factory=Session):
        self._session_factory = session_factory

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
        with self._session_factory() as db_session:
            orm = OfferORM.from_domain(offer)
            db_session.add(orm)
            db_session.commit()
            db_session.refresh(orm)
            return orm.to_domain()

    def get_by_id():
        pass

    def get_all(self):
        pass

    def delete():
        pass 

    def reset():
        pass 

    def count():
        pass
