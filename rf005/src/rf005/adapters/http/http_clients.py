from typing import List, Optional, Dict
import httpx

from ...domain.ports.ports import (
    UsersClientPort,
    PostsClientPort,
    RoutesClientPort,
    OffersClientPort,
    ScoreClientPort,
)
from ...domain.models.models import User, Post, Route, Offer
from ...errors import (
    ServiceCommunicationError,
    InvalidTokenError,
    AuthorizationError,
    EntityNotFoundError,
)

class HTTPClientBase:
    def __init__(self, base_url: str, timeout: float = 10.0):
        if not base_url:
            raise ValueError("La URL base del servicio no puede estar vacía.")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                return await client.request(method, url, **kwargs)
        except httpx.RequestError as exc:
            raise ServiceCommunicationError(f"Error de comunicación con {url}: {exc}")


class HTTPUsersClientAdapter(HTTPClientBase, UsersClientPort):
    """Adaptador HTTP para el servicio de usuarios."""
    async def get_user_from_token(self, token: str) -> Optional[User]:
        bearer = token if token.startswith("Bearer ") else f"Bearer {token}"
        resp = await self._request("GET", "/users/me", headers={"Authorization": bearer})

        ct = resp.headers.get("content-type", "")
        body = resp.json() if "application/json" in ct else {}

        if resp.status_code == 200:
            return User(**body)
        if resp.status_code == 401:
            raise InvalidTokenError(body.get("msg", "Token inválido."))
        if resp.status_code == 403:
            raise AuthorizationError(body.get("msg", "No autorizado."))
        if resp.status_code == 404:
            raise EntityNotFoundError(body.get("msg", "El usuario no existe."))
        raise ServiceCommunicationError("users")


class HTTPPostsClientAdapter(HTTPClientBase, PostsClientPort):
    """Adaptador HTTP para el servicio de Publicaciones."""
    async def get_post_by_id(self, post_id: str) -> Optional[Post]:
        resp = await self._request("GET", f"/posts/{post_id}")

        if resp.status_code == 200:
            return Post(**resp.json())
        if resp.status_code == 404:
            raise EntityNotFoundError("La publicación no existe.")
        raise ServiceCommunicationError("posts")


class HTTPRoutesClientAdapter(HTTPClientBase, RoutesClientPort):
    """Adaptador HTTP para el servicio de Rutas."""
    async def get_route_by_id(self, route_id: str) -> Optional[Route]:
        resp = await self._request("GET", f"/routes/{route_id}")

        if resp.status_code == 200:
            return Route(**resp.json())
        if resp.status_code == 404:
            raise EntityNotFoundError("El trayecto no existe.")
        raise ServiceCommunicationError("routes")


class HTTPOffersClientAdapter(HTTPClientBase, OffersClientPort):
    """Adaptador HTTP para el servicio de Ofertas."""
    async def get_offers_by_post_id(self, post_id: str) -> List[Offer]:
        resp = await self._request("GET", "/offers/", params={"post": post_id})

        if resp.status_code == 200:
            data = resp.json()
            return [Offer(**item) for item in data]
        if resp.status_code == 404:
            return []
        raise ServiceCommunicationError("offers")


class HTTPScoreClientAdapter(HTTPClientBase, ScoreClientPort):
    """Adaptador HTTP para el servicio de Scores."""

    async def get_scores_for_offers(
        self, offers: List[Offer], route: Route
    ) -> Dict[str, float]:
        """
        Obtiene los scores para una lista de ofertas haciendo una única llamada batch,
        lo cual es más eficiente que hacer una llamada por cada oferta.
        """
        if not offers:
            return {}

        # Prepara el payload para la solicitud batch al servicio de scores.
        payload = [
            {
                "offer_id": offer.id,
                "size": offer.size,
                "baggage_value": route.bagCost,
                "amount_offered": offer.offer,
            }
            for offer in offers
        ]
        resp = await self._request("POST", "/scores/", json=payload)

        # El servicio de scores devuelve 201 en caso de éxito.
        if resp.status_code == 201:
            results = resp.json()
            return {item["offer_id"]: item["score"] for item in results}

        raise ServiceCommunicationError("scores")