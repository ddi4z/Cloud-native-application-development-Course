from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


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
    @field_validator("sourceAirportCode", "destinyAirportCode")
    @classmethod
    def validate_airport_code(cls, v: str) -> str:
        """Valida que el código de aeropuerto sea un string de 3 letras y lo estandariza a mayúsculas."""
        if not v.isalpha() or len(v) != 3:
            raise ValueError(
                f"'{v}' Código de aeropuerto inválido. Debe contener 3 letras."
            )
        return v.upper()

    @field_validator("plannedStartDate")
    @classmethod
    def validate_start_date_in_future(cls, v: datetime) -> datetime:
        """Valida que la fecha de inicio no esté en el pasado."""
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        if v < datetime.now(timezone.utc):
            raise ValueError("La fecha de inicio no puede estar en el pasado.")
        return v

    @model_validator(mode="after")  # Para validar las fechas con los datos "limpios"
    def check_dates(self) -> "Trayecto":
        """Valida que la fecha de fin sea posterior a la de inicio."""
        if self.plannedEndDate <= self.plannedStartDate:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")
        return self
