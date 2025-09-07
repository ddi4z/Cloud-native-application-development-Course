from typing import List, Dict
from ...domain.models.models import User, Post, Route, Offer
from ...domain.ports.ports import (
    UsersClientPort,
    PostsClientPort,
    RoutesClientPort,
    OffersClientPort,
    ScoreClientPort,
)
from ...errors import EntityNotFoundError, InvalidTokenError

# Implementaciones mocks hechas en memoria de los clientes de API para poder probar el caso de uso de forma aislada.

class InMemoryUsersClientAdapter(UsersClientPort):
    """Adaptador mock para el servicio de usuarios."""
    def __init__(self):
        self._users: Dict[str, User] = {}  # Mapea: token -> User

    async def get_user_from_token(self, token: str) -> User:
        user = self._users.get(token)
        if not user:
            raise InvalidTokenError("Token de usuario mock no encontrado.")
        return user

class InMemoryPostsClientAdapter(PostsClientPort):
    """Adaptador mock para el servicio de publicaciones."""
    def __init__(self):
        self._posts: Dict[str, Post] = {}  # Mapea: post_id -> Post

    async def get_post_by_id(self, post_id: str) -> Post:
        post = self._posts.get(post_id)
        if not post:
            raise EntityNotFoundError("Publicación mock no encontrada.")
        return post

class InMemoryRoutesClientAdapter(RoutesClientPort):
    """Adaptador mock para el servicio de trayectos."""
    def __init__(self):
        self._routes: Dict[str, Route] = {}  # Mapea: route_id -> Route

    async def get_route_by_id(self, route_id: str) -> Route:
        route = self._routes.get(route_id)
        if not route:
            raise EntityNotFoundError("Trayecto mock no encontrado.")
        return route

class InMemoryOffersClientAdapter(OffersClientPort):
    """Adaptador mock para el servicio de ofertas."""
    def __init__(self):
        self._offers: List[Offer] = []

    async def get_offers_by_post_id(self, post_id: str) -> List[Offer]:
        return [offer for offer in self._offers if offer.postId == post_id]

class MockScoreClientAdapter(ScoreClientPort):
    """
    Implementación mock para el servicio de Score, ya que aún no está desarrollado.
    Calcula la utilidad basándose en la fórmula provista en el glosario.
    """
    def calculate_score(self, offer: Offer, route: Route) -> float:
        size_percentage_map = {
            "LARGE": 1.0,
            "MEDIUM": 0.5,
            "SMALL": 0.25,
        }
        percentage = size_percentage_map.get(offer.size.upper(), 0)

        # utilidad = monto oferta - (porcentaje de ocupación * costo de maleta)
        utility = offer.offer - (percentage * route.bagCost)
        return round(utility, 2)