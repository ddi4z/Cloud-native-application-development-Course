from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID, uuid4


class Post(BaseModel):
    """Post domain model."""
    id: UUID
    routeId: str = Field(description="Route identifier in UUID format")
    userId: str = Field(description="User Id of the user who owns the post")
    expireAt: datetime = Field(description="Date and time when post offer expires, in ISO format")
    createdAt: datetime = Field(description="Date and time when the post was created")
    




    """
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
    """

    @staticmethod
    def new(routeId: str = 'test_123', expireAt=datetime.now(timezone.utc), userId: str='user_test123') -> "Post":
        return Post(
            id = uuid4(),
            routeId=str(uuid4()),
            userId=str(uuid4()),
            expireAt=datetime.now(timezone.utc),
            createdAt=datetime.now(timezone.utc),
        )