from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class UserCallbackRequest(BaseModel):
    RUV: str
    userIdentifier: str
    createdAt: datetime
    status: Literal["POR_VERIFICAR", "VERIFICADO", "NO_VERIFICADO"]
    score: float
    verifyToken: str
