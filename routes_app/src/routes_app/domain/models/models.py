from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Trayecto(BaseModel):
    """
    Modelo de dominio para la entidad Trayecto.
    Campos según especificación del proyecto (Vista de información).
    """
    id: UUID = Field(default_factory=uuid4)
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: datetime
    plannedEndDate: datetime
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))