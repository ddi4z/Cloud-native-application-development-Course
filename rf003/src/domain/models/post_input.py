from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostInput(BaseModel):
    title: str
    description: Optional[str] = None
    expires_at: datetime