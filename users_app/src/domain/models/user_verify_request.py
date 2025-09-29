from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserData(BaseModel):
    email: EmailStr = Field(description="User email address in valid format")
    dni: Optional[str] = Field(
        default=None, description="User DNI (National Identity Document)"
    )
    fullName: Optional[str] = Field(default=None, description="User full name")
    phone: Optional[str] = Field(default=None, description="User phone number")


class UserVerifyRequest(BaseModel):
    user: UserData
    transactionIdentifier: str = Field(
        description="Unique value defined by the client for traceability"
    )
    userIdentifier: str = Field(
        description="Unique identifier for the user in the client system"
    )
    userWebhook: str = Field(
        description="Webhook URL where verification results will be notified"
    )
