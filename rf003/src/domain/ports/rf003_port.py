from abc import ABC, abstractmethod
from __future__ import annotations
from typing import Protocol, Optional
from src.domain.models.models import Post, Route


from src.domain.models.models import RouteOrigin, CreatePost

class UsersPort(Protocol):
    def get_user_from_token(self, token: str) -> str: ...  # returns user_id

class RoutesPort(Protocol):
    def find_route_by_flightid(self, flightId: str) -> Optional[str]: ...
    def get_or_create_route(self, route: RouteOrigin) -> str: ...

class PostsPort(Protocol):
    def get_post_from_userid_route_id(self, user_id: str, route_id: str) -> bool: ...
    def create_post(self, create_post_dto: CreatePost) -> str: ...



class ANOTHERPostsPort(ABC):
    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def get_post_by_user_and_route(self, user_id: str, route_id: str) -> Post:
        """
        Retrieves a post for a given user and route.
        """
        raise NotImplementedError
    

class ANOTHERRoutesPort(ABC):
    @abstractmethod
    async def get_or_create_route(self, route_data: Route) -> Route:
        """
        Checks if a route exists. If it does, returns the existing route.
        If not, it creates a new one and returns it.
        """
        raise NotImplementedError