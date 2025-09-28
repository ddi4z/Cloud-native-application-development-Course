from datetime import datetime
from pydantic import BaseModel
from src.domain.models.credit_card import CreditCardIssuer, CreditCardStatus

class CreditCardCreatedResponse(BaseModel):
    id: str
    userId: str
    createdAt: datetime

class CreditCardPublic(BaseModel):
    id: str
    token: str               
    userId: str
    lastFourDigits: str
    issuer: CreditCardIssuer
    status: CreditCardStatus
    createdAt: datetime
    updatedAt: datetime