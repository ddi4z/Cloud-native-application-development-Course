from src.domain.ports.post_validation_port import PostValidationPort
from typing import Optional
from src.domain.models.post import Post
import requests
from requests.models import Response
from src.errors import UnavailableService
from .catch_unavailable_service import catch_unavailable_service

class PostValidationAdapter(PostValidationPort):
    """"""
    def __init__(self, post_service_url: str):
        self.post_service_url = post_service_url
    
    @catch_unavailable_service("Post")
    def validate_and_get_post(self, postId: str) -> Optional[Post]:
        """Validate the postId and get the post. If the postId is invalid, return None."""
        response = requests.get(
            f"{self.post_service_url}/{postId}",
        )

        if response.status_code != 200:
            return None
        
        post_response = Post(**response.json())

        return post_response

    @catch_unavailable_service("Post")
    def ping(self) -> None:
        response: Response = requests.get(self.post_service_url + "/ping")
        if response.status_code != 200:
            raise UnavailableService("Post service is not working")
