from typing import Optional
from pydantic import BaseModel


class ScoreRequest(BaseModel):
    offer_id: str
    size: str
    baggage_value: float
    amount_offered: float
