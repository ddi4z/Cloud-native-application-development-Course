from abc import ABC, abstractmethod
from typing import Protocol, Optional, List
from src.domain.models.models import User, Route, Post, CreatedRoute, RouteCreateInput, CreatePost, CreatedPost
#Post, CreatePost, UserGetResponse, RouteGetResponse, RouteCreateInput, RouteCreateResponse, CreatePostResponse


class HttpRequest(ABC):
    """Post repository interface."""

    @abstractmethod
    def ping(self) -> bool:
        """Create a new post."""
        raise NotImplementedError("This method should be overridden in subclasses")


class UsersPort(HttpRequest):
    "User Rep inter"

    @abstractmethod
    def get_user_from_token(self, token:str) -> Optional[User]:
        " Get user from token"
        raise NotImplementedError("This method should be overriden in subclasses")

class RoutesPort(HttpRequest):
    "User Rep inter"

    @abstractmethod
    def find_route_by_flight_id(self, flightId:str) -> Optional[Route]:
        " Get user from token"
        raise NotImplementedError("This method should be overriden in subclasses")
    
    @abstractmethod
    def create_route(self, route_dto:RouteCreateInput) -> Optional[CreatedRoute]:
        " Get user from token"
        raise NotImplementedError("This method should be overriden in subclasses")

class PostsPort(HttpRequest):

    @abstractmethod
    def get_post_from_userid_route_id(self, user_id: str, route_id: str) -> Optional[List[Post]]:
        " Get user from token"
        raise NotImplementedError("This method should be overriden in subclasses")
    
    @abstractmethod
    def create_post(self, create_post_dto: CreatePost) -> Optional[CreatedPost]:
        " Get user from token"
        raise NotImplementedError("This method should be overriden in subclasses")
    
    
    
