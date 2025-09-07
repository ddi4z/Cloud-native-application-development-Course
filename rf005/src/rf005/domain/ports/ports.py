from abc import ABC, abstractmethod
from typing import List
from ..models import User, Post, Route, Offer

class APIClientPort(ABC):
    """Base port for external service clients."""
    pass

class UsersClientPort(APIClientPort):
    @abstractmethod
    async def get_user_from_token(self, token: str) -> User:
        raise NotImplementedError

class PostsClientPort(APIClientPort):
    @abstractmethod
    async def get_post_by_id(self, post_id: str) -> Post:
        raise NotImplementedError

class RoutesClientPort(APIClientPort):
    @abstractmethod
    async def get_route_by_id(self, route_id: str) -> Route:
        raise NotImplementedError

class OffersClientPort(APIClientPort):
    @abstractmethod
    async def get_offers_by_post_id(self, post_id: str) -> List[Offer]:
        raise NotImplementedError

class ScoreClientPort(APIClientPort):
    @abstractmethod
    def calculate_score(self, offer: Offer, route: Route) -> float:
        """This is mocked, so it can be synchronous."""
        raise NotImplementedError