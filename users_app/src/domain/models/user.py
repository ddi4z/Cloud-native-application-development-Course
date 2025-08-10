from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class UserStatus(str, Enum):
    """Enum for user status."""
    PENDING_VERIFICATION = "POR_VERIFICAR"
    NOT_VERIFIED = "NO_VERIFICADO"
    VERIFIED = "VERIFICADO"

class User(BaseModel):
    """User domain model."""
    id: str = Field(description="User identifier in UUID format")
    username: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$", description="Username without spaces or special characters")
    email: EmailStr = Field(description="User email address in valid format")
    phoneNumber: Optional[str] = Field(description="Phone number for contact")
    dni: Optional[str] = Field(description="National ID number")
    fullName: Optional[str] = Field(description="Full name of the user")
    password: str = Field(description="Hashed password")
    salt: str = Field(description="Salt used for password hashing")
    token: str = Field(description="Current authentication token")
    status: UserStatus = Field(description="Current user status")
    expireAt: datetime = Field(description="Date and time when the token expires")
    createdAt: datetime = Field(description="Date and time when the user was created")
    updatedAt: datetime = Field(description="Date and time when the user was last updated")