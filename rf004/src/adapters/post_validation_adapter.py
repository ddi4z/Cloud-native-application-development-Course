from src.domain.ports.post_validation_port import PostValidationPort
from typing import Optional
from src.domain.models.post import Post
import requests

class PostValidationAdapter(PostValidationPort):
    """"""
    def __init__(self, post_service_url: str):
        self.post_service_url = post_service_url
    
    def validate_and_get_post(self, postId: str) -> Optional[Post]:
        """Validate the postId and get the post. If the postId is invalid, return None."""
        response = requests.get(
            f"{self.post_service_url}/{postId}",
        )

        if response.status_code != 200:
            return None
        
        post_response = Post(**response.json())

        return post_response
