from pydantic import BaseModel

class RouteBagCost(BaseModel):
    """Score domain model."""

    bagCost: int
