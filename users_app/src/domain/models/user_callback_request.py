from typing import Literal
from datetime import datetime
from pydantic import BaseModel


class UserCallbackRequest(BaseModel):
    RUV: str
    userIdentifier: str
    createdAt: datetime
    status: Literal["POR_VERIFICAR", "VERIFICADO", "NO_VERIFICADO"]
    score: int
    verifyToken: str
