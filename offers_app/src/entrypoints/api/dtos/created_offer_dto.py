import uuid
from pydantic import BaseModel

class CreatedOfferDto(BaseModel):
    """Offer domain model."""

    id: uuid.UUID | None = None
    userId: str = None
    createdAt: str = None