from src.domain.ports.user_validation_port import UserValidationPort
import requests
from src.domain.models.user import User
from typing import Optional
from requests.models import Response
from src.errors import UnavailableService

from .catch_unavailable_service import catch_unavailable_service
class UserValidationAdapter(UserValidationPort):
    """Implementation of UserValidationPort to orchestrate the validation of a user."""

    def __init__(self, user_service_url: str):
        self.user_service_url = user_service_url

    @catch_unavailable_service("Users")
    def validate_token_and_get_user(self, token: str) -> Optional[User]:
        """Validate the auth token and get the user. If the token is invalid, return None."""
        response: Response = requests.get(
            f"{self.user_service_url}/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            return None
        
        user_response = User(**response.json())

        return user_response
    
    @catch_unavailable_service("Users")
    def ping(self) -> None:
        response: Response = requests.get(f"{self.user_service_url}/ping")
        if response.status_code != 200:
            raise UnavailableService("Users service is not working")
