from pydantic import BaseModel


class Post(BaseModel):
    """Post domain model."""

    id: str
    routeId: str
    userId: str
    expireAt: str # 2025-09-18T02:04:26.637Z
    createdAt: str # 2025-09-18T02:04:26.637Z
