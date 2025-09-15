from functools import wraps
from requests.exceptions import RequestException
import httpx 
from typing import List, Optional
import logging

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort, RouteCreateInput
from src.domain.models.models import User, Route, Post, CreatedRoute, CreatedPost, CreatePost
from src.errors import ServiceCommunicationError

logger = logging.getLogger(__name__)

def catch_unavailable_service(service_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs): 
            try:
                return await func(*args, **kwargs) 
            except (httpx.RequestError, httpx.ConnectError, httpx.TimeoutException) as e: 
                logger.error(f"Error comunicando con {service_name}: {e}")
                raise ServiceCommunicationError(f'{service_name} service is not available')
        return wrapper
    return decorator


class HTTPClientBase:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, follow_redirects=True)

    async def close(self):
        await self.client.aclose()


# Users
class HTTPRoutesClientAdapter(HTTPClientBase, RoutesPort):
    """Implementation of RoutesPort."""

    def __init__(self, route_service_url: str):
        super().__init__(base_url=route_service_url)

    @catch_unavailable_service("Routes")
    async def find_route_by_flight_id(self, flightId: str) -> Optional[Route]:
        # ✅ usa /routes/ (con slash) para evitar 307
        params = {"flight": flightId}
        response = await self.client.get("/routes/", params=params)
        
        if response.status_code != 200:
            return None
        
        items = response.json() or []
        items = [r for r in items if r.get("flightId") == flightId]
        return Route(**items[0]) if items else None

    @catch_unavailable_service("Routes")
    async def create_route(self, route_dto: RouteCreateInput) -> Optional[CreatedRoute]:
        # ✅ usa /routes/ (con slash) para evitar 307
        response = await self.client.post("/routes/", json=route_dto.model_dump())

        if response.status_code == 201:
            return CreatedRoute(**response.json())

        if response.status_code == 412 and "flightId ya existe" in (response.text or ""):
            import logging
            logging.getLogger(__name__).warning(
                "[RF003->ROUTES] POST /routes/ respondió 412 (flightId ya existe). "
                "Intentando recuperar trayecto existente..."
            )
            existing = await self.find_route_by_flight_id(route_dto.flightId)
            if existing:
                return CreatedRoute(**existing.model_dump())
            logging.getLogger(__name__).error(
                "[RF003->ROUTES] 412 recibido pero no se pudo recuperar el trayecto por flightId."
            )
            return None

        import logging
        logging.getLogger(__name__).error(
            f"[RF003->ROUTES] POST /routes/ devolvió {response.status_code}: {response.text}"
        )
        return None

    @catch_unavailable_service("Routes")
    async def ping(self) -> None:
        # /routes/ping no cambia
        response = await self.client.get("/routes/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Routes service is not working")

    
    @catch_unavailable_service("Routes")
    async def ping(self) -> None:
        response = await self.client.get("/routes/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Routes service is not working")



# Posts
class HTTPPostsClientAdapter(HTTPClientBase, PostsPort):
    """Implementation of PostsPort."""
    def __init__(self, post_service_url: str):
        super().__init__(base_url=post_service_url)

    async def get_post_from_userid_route_id(self, user_id: str, route_id: str) -> Optional[List[Post]]:
        # En query params, usa strings
        params = {"route": str(route_id), "owner": str(user_id)}
        # Mejor con slash final para evitar 307 si el router lo exige
        response = await self.client.get("/posts/", params=params)

        if response.status_code != 200:
            return []

        raw = response.json() or []
        normalized: List[Post] = []

        for item in raw:
            d = dict(item)
            # Normaliza nombres de campos según lo que envíe posts_app
            if "ownerId" not in d and "userId" in d:
                d["ownerId"] = d["userId"]
            # (si tu modelo Post usa "id", "routeId", "createdAt" etc., no hace falta tocar)
            normalized.append(Post(**d))

        return normalized

    @catch_unavailable_service('Posts')
    async def create_post(self, create_post_dto: CreatePost) -> Optional[CreatedPost]:
        payload = create_post_dto.model_dump(mode="json")
        response = await self.client.post("/posts/", json=payload)

        if response.status_code == 201:
            return CreatedPost(**response.json())

        # Duplicado: usuario ya tiene publicación para ese trayecto/fecha
        if response.status_code in (409, 412):
            from src.errors import ConflictError
            raise ConflictError("El usuario ya tiene una publicación para la misma fecha")

        import logging
        logging.getLogger(__name__).error(
            f"[RF003->POSTS] POST /posts/ devolvió {response.status_code}: {response.text}"
        )
        return None

    @catch_unavailable_service("Posts")
    async def ping(self) -> None: 
        response = await self.client.get("/posts/ping") 
        if response.status_code != 200:
            raise ServiceCommunicationError("Posts service is not working")

class HTTPUsersClientAdapter(HTTPClientBase, UsersPort):
    """Implementation of UsersPort."""

    def __init__(self, user_service_url: str):
        super().__init__(base_url=user_service_url)

    @catch_unavailable_service("Users")
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Valida token y obtiene el usuario. Devuelve None si el token es inválido."""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.get("/users/me", headers=headers)
        if response.status_code != 200:
            return None
        return User(**response.json())

    @catch_unavailable_service("Users")
    async def ping(self) -> None:
        response = await self.client.get("/users/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Users service is not working")