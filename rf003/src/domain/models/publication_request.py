from pydantic import BaseModel
from src.domain.models.post_input import PostInput
from src.domain.models.route_input import RouteInput

class PublicationRequest(BaseModel):
    post: PostInput
    route: RouteInput