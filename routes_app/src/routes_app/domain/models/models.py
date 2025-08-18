from pydantic import BaseModel, Field
from typing import List
from uuid import UUID, uuid4

class Stop(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    lat: float
    lon: float

class Route(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    stops: List[Stop] = []