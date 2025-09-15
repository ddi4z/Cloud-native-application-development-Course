# src/rf005/domain/ports/ports.py

from abc import ABC, abstractmethod
from typing import List, Dict
from ..models.models import User, Post, Route, Offer

class APIClientPort(ABC):
    """Puerto base para los clientes de API."""
    pass


class UsersClientPort(APIClientPort):
    @abstractmethod
    async def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_from_token(self, token: str) -> User:
        raise NotImplementedError


class PostsClientPort(APIClientPort):
    @abstractmethod
    async def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_post_by_id(self, post_id: str) -> Post:
        raise NotImplementedError


class RoutesClientPort(APIClientPort):
    @abstractmethod
    async def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_route_by_id(self, route_id: str) -> Route:
        raise NotImplementedError


class OffersClientPort(APIClientPort):
    @abstractmethod
    async def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_offers_by_post_id(self, post_id: str) -> List[Offer]:
        raise NotImplementedError


class ScoreClientPort(APIClientPort):
    @abstractmethod
    async def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_scores_for_offers(
        self, offers: List[Offer], route: Route
    ) -> Dict[str, float]:
        """
        Obtiene los scores para una lista de ofertas y los devuelve en un mapa.
        """
        raise NotImplementedError
