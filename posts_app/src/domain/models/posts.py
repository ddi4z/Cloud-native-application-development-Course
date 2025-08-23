from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Post(BaseModel):
    """Post domain model."""

    id: UUID
    routeId: UUID = Field(description="Route identifier in UUID format")
    userId: UUID = Field(description="User Id of the user who owns the post")
    expireAt: datetime = Field(
        description="Date and time when post offer expires, in ISO format"
    )
    createdAt: datetime = Field(description="Date and time when the post was created")
