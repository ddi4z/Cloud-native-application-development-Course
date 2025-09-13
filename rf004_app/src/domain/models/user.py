from pydantic import BaseModel


class User(BaseModel):
    """User domain model."""

    id: str
    username: str
    email: str
    fullName: str
    dni: str
    phoneNumber: str
    status: str