from __future__ import annotations
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class Location(BaseModel):
    airportCode: str
    country: str

    @field_validator("airportCode")
    @classmethod
    def validate_airport_code(cls, v: str) -> str:
        # Código IATA de 3 letras
        if not isinstance(v, str) or len(v) != 3 or not v.isalpha():
            raise ValueError("Código de aeropuerto inválido. Debe contener 3 letras.")
        return v.upper()

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("El país es requerido.")
        return v.strip()

class UserInput(BaseModel):
    """
    Payload de entrada del RF003 (crear publicación).
    Se mantiene el tipo str para fechas porque el use case hace fromisoformat().
    """
    flightId: str
    origin: Location
    destiny: Location
    bagCost: int
    plannedStartDate: str  
    plannedEndDate: str    
    expireAt: str           

    @field_validator("flightId")
    @classmethod
    def validate_flight_id(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("flightId es requerido.")
        return v.strip()

    @field_validator("bagCost")
    @classmethod
    def validate_bag_cost(cls, v: int) -> int:
        if v is None or v < 0:
            raise ValueError("bagCost debe ser un entero >= 0.")
        return v

    @staticmethod
    def _validate_iso8601(s: str, field_name: str) -> str:
        try:
            datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            raise ValueError(f"{field_name} debe tener formato de fecha ISO-8601.")
        return s

    @field_validator("plannedStartDate")
    @classmethod
    def validate_start_iso(cls, v: str) -> str:
        return cls._validate_iso8601(v, "plannedStartDate")

    @field_validator("plannedEndDate")
    @classmethod
    def validate_end_iso(cls, v: str) -> str:
        return cls._validate_iso8601(v, "plannedEndDate")

    @field_validator("expireAt")
    @classmethod
    def validate_expire_iso(cls, v: str) -> str:
        return cls._validate_iso8601(v, "expireAt")

class RouteCreateInput(BaseModel):
    """
    Debe coincidir con routes_app.TrayectoIn:
      - flightId: str
      - sourceAirportCode: str
      - sourceCountry: str
      - destinyAirportCode: str
      - destinyCountry: str
      - bagCost: int
      - plannedStartDate: datetime (acepta ISO string)
      - plannedEndDate: datetime  (acepta ISO string)
    """
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: str 
    plannedEndDate: str   

    @field_validator("sourceAirportCode", "destinyAirportCode")
    @classmethod
    def airports_are_iata(cls, v: str) -> str:
        if not isinstance(v, str) or len(v) != 3 or not v.isalpha():
            raise ValueError("Código de aeropuerto inválido. Debe contener 3 letras.")
        return v.upper()

    @field_validator("sourceCountry", "destinyCountry")
    @classmethod
    def countries_are_nonempty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("El país es requerido.")
        return v.strip()

    @field_validator("bagCost")
    @classmethod
    def bag_cost_nonnegative(cls, v: int) -> int:
        if v is None or v < 0:
            raise ValueError("bagCost debe ser un entero >= 0.")
        return v

    @field_validator("plannedStartDate", "plannedEndDate")
    @classmethod
    def validate_dates_iso(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("Las fechas deben tener formato ISO-8601.")
        return v

class CreatePost(BaseModel):
    """
    Contrato de entrada hacia posts_app:
      routeId: UUID
      expireAt: str (ISO-8601)
      userId: UUID
    """
    routeId: UUID
    expireAt: str
    userId: UUID

    @field_validator("expireAt")
    @classmethod
    def validate_expire_iso(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("expireAt debe tener formato de fecha ISO-8601.")
        return v


class CreatedPost(BaseModel):
    """
    Contrato de salida de posts_app (201):
      id: UUID
      userId: UUID
      createdAt: str/datetime (lo dejamos como str para no forzar conversión)
    """
    id: UUID
    userId: UUID
    createdAt: str

class Route(BaseModel):
    """
    Representa el trayecto tal como lo entrega routes_app en TrayectoOut.
    """
    id: UUID = Field(default_factory=uuid4)
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: str
    plannedEndDate: str
    createdAt: str
    updatedAt: str


class Post(BaseModel):
    """
    Representación mínima de un Post para listados (GET /posts?route=...&owner=...).
    Ajusta campos según tu posts_app si necesitas más.
    """
    id: UUID
    routeId: UUID
    ownerId: UUID
    createdAt: str

class RouteDetails(BaseModel):
    id: UUID
    flightId: str
    createdAt: str

class PublicationResponseData(BaseModel):
    id: UUID          # id del post
    userId: UUID      # dueño del post
    createdAt: str    # fecha de creación del post
    route: RouteDetails

class PublicationResponse(BaseModel):
    msg: str
    data: PublicationResponseData

class User(BaseModel):
    """
    Estructura esperada por RF003 al validar token contra users_app.
    Campos vistos en logs: id, username, email, fullName, dni, phoneNumber, status.
    """
    id: UUID
    username: str
    email: str
    fullName: str
    dni: str
    phoneNumber: str
    status: str

class CreatedRoute(Route):
    pass
