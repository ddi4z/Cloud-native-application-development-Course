from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PostCreationRequest(BaseModel):
    routeId: UUID = None
    expireAt: datetime = None
    userId: UUID = None
