from pydantic import BaseModel
from datetime import datetime

class RouteInput(BaseModel):
    origin: str
    destination: str
    departure_at: datetime # debe estar en el futuro