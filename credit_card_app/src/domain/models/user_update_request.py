from typing import Optional

from pydantic import BaseModel


class UserUpdateRequest(BaseModel):
    status: Optional[str] = None
    dni: Optional[str] = None
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None
