from src.domain.ports.user_validation_port import UserValidationPort
import requests
from src.domain.models.user import User
from typing import Optional
from requests.models import Response

class UserValidationAdapter(UserValidationPort):
    """Implementation of UserValidationPort to orchestrate the validation of a user."""

    def __init__(self, user_service_url: str):
        self.user_service_url = user_service_url

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
    