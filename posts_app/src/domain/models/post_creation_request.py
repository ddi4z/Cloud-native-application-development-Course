from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PostCreationRequest(BaseModel):
  routeId: Optional[str] = ""
  expireAt: Optional[datetime] = None
  userId: Optional[str] = ""