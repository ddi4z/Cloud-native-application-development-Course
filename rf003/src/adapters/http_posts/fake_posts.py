from src.domain.ports.rf003_port import PostsPort
from src.domain.models.publication_request import PublicationRequest

class FakePosts(PostsPort):
    def __init__(self): self.by_user_route = set()
    def user_has_post_for_route(self, user_id: str, route_id: str) -> bool:
        return (user_id, route_id) in self.by_user_route
    def create(self, user_id: str, route_id: str, req: PublicationRequest) -> str:
        self.by_user_route.add((user_id, route_id))
        return f"post-{len(self.by_user_route)}"