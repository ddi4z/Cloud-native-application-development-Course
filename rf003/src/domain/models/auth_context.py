from pydantic import BaseModel

class AuthContext(BaseModel):
    user_id: str | None = None
    token: str