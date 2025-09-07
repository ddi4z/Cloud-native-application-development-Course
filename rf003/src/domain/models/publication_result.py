from pydantic import BaseModel
from datetime import datetime

class PublicationResult(BaseModel):
    post_id: str
    route_id: str
    user_id: str
    created_at: datetime