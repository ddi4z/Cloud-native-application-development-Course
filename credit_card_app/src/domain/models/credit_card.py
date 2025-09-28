from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreditCardStatus(str, Enum):
    """Enum for cc status."""

    PENDING_VERIFICATION = "POR_VERIFICAR"
    REJECTED = "RECHAZADA"
    APPROVED = "APROBADA"


class CreditCardIssuer(str, Enum):
    """Enum for Credit Card Issuers"""
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN EXPRESS"
    DISCOVER = "DISCOVER"
    DINERS_CLUB = "DINERS CLUB"
    UNKNOWN = "UNKNOWN"


class CreditCard(BaseModel):
    """Modelo de dominio para CreditCard"""

    id: str = Field(description="Identificador en formato UUID")
    token: str = Field(min_length=1, max_length=256, description="Token generado por la plataforma de pagos (256 chars)")
    userId: str = Field(description="Usuario propietario de la tarjeta de crédito, en formato UUID")
    lastFourDigits: str = Field(description="Últimos cuatro dígitos de la tarjeta de crédito", min_length=4, max_length=4)
    ruv: str = Field(description="Registro único de verificación")
    issuer: CreditCardIssuer = Field(description="Emisor de la tarjeta de crédito")
    status: CreditCardStatus = Field(description="Estado actual de la tarjeta de crédito")
    createdAt: datetime = Field(description="Fecha y hora en que se creó la tarjeta de crédito")
    updatedAt: datetime = Field(description="Fecha y hora en que se actualizó la tarjeta de crédito")

    class Config:
        from_attributes = True