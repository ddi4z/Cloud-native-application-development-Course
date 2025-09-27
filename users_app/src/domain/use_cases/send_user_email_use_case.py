from src.domain.models.user import User
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.ports import message_queue_port


class SendUserEmailUseCase(BaseUseCase):
    """Use case for sending a user email."""

    def __init__(self, message_queue_port: message_queue_port):
        self.message_queue_port = message_queue_port

    def execute(self, user: User) -> None:
        """Patch an existing user."""
        return self.message_queue_port.send_message(user)
