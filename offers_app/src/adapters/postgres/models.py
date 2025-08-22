import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String
from sqlalchemy import String

from src.domain.models.offer import Offer, OfferSize

from .db_config import Base


class OfferORM(Base):
    """Offer table in PostgreSQL."""

    __tablename__ = "offers"

    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False
    )
    post_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)

    description = Column(String, nullable=False)
    size = Column(SqlEnum(OfferSize), nullable=False)
    fragile = Column(Boolean, nullable=False)
    offer = Column(Integer, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<OfferORM(id={self.id}, post_id={self.post_id}, user_id={self.user_id}, "
            f"size={self.size}, offer={self.offer}, created_at={self.created_at})>"
        )

    # ---------- Mapeos ----------

    def to_domain(self) -> Offer:
        """Convierte la entidad ORM a modelo de dominio (Pydantic)."""
        return Offer(
            id=str(self.id),
            postId=str(self.post_id),
            userId=str(self.user_id),
            description=self.description,
            size=str(self.size),
            fragile=self.fragile,
            offer=self.offer,
            createdAt=(
                self.created_at.isoformat(timespec="seconds")
                if self.created_at
                else None
            ),
        )

    @classmethod
    def from_domain(cls, offer: Offer) -> "OfferORM":
        """Convierte un modelo de dominio (Pydantic) a entidad ORM."""
        return cls(
            id=offer.id if offer.id else str(uuid.uuid4()),
            post_id=offer.postId,
            user_id=offer.userId,
            description=offer.description,
            size=OfferSize(offer.size),
            fragile=offer.fragile,
            offer=offer.offer,
            created_at=(
                datetime.datetime.fromisoformat(offer.createdAt)
                if offer.createdAt
                else datetime.datetime.utcnow()
            ),
        )
