from typing import Optional
from pydantic import BaseModel

class UserCreationRequest(BaseModel):
  username: str
  password: str
  email: str
  dni: Optional[str]
  fullName: Optional[str]
  phoneNumber: Optional[str]
