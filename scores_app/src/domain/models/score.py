from pydantic import BaseModel, Field

class Score(BaseModel):
    """Score domain model."""
    offer_id: str = Field(description="Offer identifier in UUID format")
    value: int = Field(description="Score value")