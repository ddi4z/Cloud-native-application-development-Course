from typing import Any
from abc import ABC, abstractmethod
from src.domain.use_cases.base_use_case import BaseUseCase

class CreatePostUseCase(ABC):
    """
    Orchestrator use case for creating a post. It communicates with other microservices
    to create the post in the system.
    """
    
    @abstractmethod
    def execute(self, user_id: str, content: str) -> Any:
        """
        Executes the process of creating a post by calling the microservice responsible
        for actually creating the post.
        
        :param user_id: ID of the user creating the post
        :param content: Content of the post to be created
        :return: Response from the post creation service
        """

        pass
