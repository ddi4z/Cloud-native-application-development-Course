from abc import ABC, abstractmethod
from typing import Protocol, Optional, List
from src.domain.models.models import Post, CreatePost, UserGetResponse, RouteGetResponse, RouteCreateInput, RouteCreateResponse, CreatePostResponse

class UsersPort(Protocol):
    def get_user_from_token(self, token: str) -> UserGetResponse: ...  # returns user_id

class RoutesPort(Protocol):
    def find_route_by_flightid(self, flightId: str) -> Optional[List[RouteGetResponse]]: ...
    def create_route(self, route_dto: RouteCreateInput) -> Optional[RouteCreateResponse]: ...

class PostsPort(Protocol):
    def get_post_from_userid_route_id(self, user_id: str, route_id: str) -> Optional[List[Post]]: ...
    def create_post(self, create_post_dto: CreatePost) -> CreatePostResponse: ...
