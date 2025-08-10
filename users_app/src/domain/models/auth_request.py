from typing import Optional
from pydantic import BaseModel

class AuthRequest(BaseModel):
    username: Optional[str] = ''
    password: Optional[str] = ''