from typing import List, Optional
import httpx

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort

from src.domain.models.models import UserInput, CreatePost, RouteCreateInput, UserGetResponse, RouteGetResponse, RouteCreateResponse, Post, CreatePostResponse, PublicationResponseData, PublicationResponse

from src.errors import ValidationError, InvalidTokenError, NoTokenError, InvalidRouteDatesError, InvalidExpiredAtError, ConflictError, ServiceCommunicationError, AuthorizationError, EntityNotFoundError




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
        

class HTTPUsersClientAdapter(HTTPClientBase, UsersPort):
    """Adaptador HTTP para el servicio de usuarios."""
    async def get_user_from_token(self, token: str) -> UserGetResponse:
        bearer = token if token.startswith("Bearer ") else f"Bearer {token}"
        resp = await self._request("GET", "/users/me", headers={"Authorization": bearer})

        ct = resp.headers.get("content-type", "")
        body = resp.json() if "application/json" in ct else {}

        if resp.status_code == 200:
            return UserGetResponse(**body)
        elif resp.status_code == 401:
            raise InvalidTokenError(body.get("msg", "Token inválido."))
        elif resp.status_code == 403:
            raise AuthorizationError(body.get("msg", "No autorizado."))
        elif resp.status_code == 404:
            raise EntityNotFoundError(body.get("msg", "El usuario no existe."))
        else:
            raise ServiceCommunicationError("users")
    

    
class HTTPRoutesClientAdapter(HTTPClientBase, RoutesPort):
    """Adaptador HTTP para el servicio de Rutas."""
    async def get_route_by_flightid(self, route_id: str) -> Optional[List[RouteGetResponse]]:
        resp = await self._request("GET", f"/routes/{route_id}")

        if resp.status_code == 200:
            return RouteGetResponse(**resp.json())
        elif resp.status_code == 404:
            raise EntityNotFoundError("El trayecto no existe.")
        else: 
            raise ServiceCommunicationError("routes")
    
    async def create_route(self, route_dto: RouteCreateInput) -> Optional[RouteCreateResponse]:
        try:
            json_data = route_dto.model_dump_json()
            resp = await self._request("POST", "/routes", data=json_data, headers={"Content-Type": "application/json"})

            if resp.status_code == 201:  # 201 Created is the standard for successful creation
                return RouteGetResponse(**resp.json())
            
            # Handle specific error cases from the service
            elif resp.status_code == 400:
                raise ValidationError("Los datos de entrada no son válidos.")
            
            elif resp.status_code == 412:
                raise ConflictError("Trayecto ya existe o fechas son incorrectas.")
            
        except Exception:
            raise ServiceCommunicationError(f"routes. Status code: {resp.status_code}")




class HTTPPostsClientAdapter(HTTPClientBase, PostsPort):
    """Adaptador HTTP para el servicio de Publicaciones."""
    async def get_post_from_userid_route_id(self, user_id: str, route_id: str) -> Optional[List[Post]]:
        params = {"owner": user_id, "route": route_id}
        resp = await self._request("GET", "/posts", params=params)

        if resp.status_code == 200:
            data = resp.json() or []
            return [Post(**item) for item in data]
        elif resp.status_code == 400:
            raise ValidationError("Invalid query parameters.")
        
        else:
            raise ServiceCommunicationError("Servicio temporalmente fuera servicio.") 