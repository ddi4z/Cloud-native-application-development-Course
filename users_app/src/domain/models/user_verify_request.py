from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserVerifyRequest(BaseModel):
    email: EmailStr = Field(description="User email address in valid format")
    dni: Optional[str] = Field(
        default=None, description="User DNI (National Identity Document)"
    )
    fullName: Optional[str] = Field(default=None, description="User full name")
    phone: Optional[str] = Field(default=None, description="User phone number")
