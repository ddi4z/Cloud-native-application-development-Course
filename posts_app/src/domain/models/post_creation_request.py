from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class PostCreationRequest(BaseModel):
  routeId: UUID = None
  expireAt: datetime = None
  userId: UUID = None