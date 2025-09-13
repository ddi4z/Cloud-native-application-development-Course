from pydantic import BaseModel


class Score(BaseModel):
    """Score domain model."""

    offer_id: str
    size: str
    baggage_value: int
    amount_offered: int
