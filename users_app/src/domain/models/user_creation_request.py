from typing import Optional
from pydantic import BaseModel

class UserCreationRequest(BaseModel):
  username: Optional[str] = ""
  password: Optional[str] = ""
  email: Optional[str] = ""
  dni: Optional[str] = None
  fullName: Optional[str] = None
  phoneNumber: Optional[str] = None
