from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from uuid import UUID, uuid4


class Trayecto(BaseModel):
    """
    Modelo de dominio para la entidad Trayecto.
    Este modelo encapsula las reglas de negocio para un Trayecto 
    según se especifica en la Vista de Información
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

    # Validadores de campos
    @field_validator('sourceAirportCode', 'destinyAirportCode')
    @classmethod
    def validate_airport_code(cls, v: str) -> str:
        """Valida que el código de aeropuerto sea un string de 3 letras y lo estandariza a mayúsculas."""
        if not v.isalpha() or len(v) != 3:
            raise ValueError(f"'{v}' Código de aeropuerto inválido. Debe contener 3 letras.")
        return v.upper()

    @model_validator(mode='after')
    def check_dates(self) -> 'Trayecto':
        """Valida que la fecha de fin planeada sea posterior a la de inicio."""
        if self.plannedEndDate <= self.plannedStartDate:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")
        return self 