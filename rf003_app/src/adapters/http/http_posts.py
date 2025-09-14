from functools import wraps
from requests.exceptions import RequestException
from requests.models import Response
import requests
from typing import List, Optional
# import httpx

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort, RouteCreateInput

from src.domain.models.models import User, Route, Post, CreatedRoute, CreatedPost, CreatePost
#UserInput, CreatePost, RouteCreateInput, UserGetResponse, RouteGetResponse, RouteCreateResponse, Post, CreatePostResponse, PublicationResponseData, PublicationResponse

from src.errors import ValidationError, InvalidTokenError, NoTokenError, InvalidRouteDatesError, InvalidExpiredAtError, ConflictError, ServiceCommunicationError, AuthorizationError, EntityNotFoundError

def catch_unavailable_service(service_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (RequestException, ConnectionError, TimeoutError) as _:
                raise ServiceCommunicationError(f'{service_name} service is not available')
        return wrapper
    return decorator



# Users
class HTTPUsersClientAdapter(UsersPort):
    "Implementation of UsersPort."

    def __init__(self, user_service_url: str):
        self.user_service_url = user_service_url

    @catch_unavailable_service("Users")
    def get_user_from_token(self, token:str) -> Optional[User]:
        "Validate token and get user. Return None if token invalid"
        response: Response = requests.get(
            f"{self.user_service_url}/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            return None

        user_response = User(**response.json())

        return user_response
    
    @catch_unavailable_service("Users")
    def ping(self) -> None:
        response: Response = requests.get(f"{self.user_service_url}/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Users service is not working")
        






class HTTPRoutesClientAdapter(RoutesPort):
    """Implementation of RoutesPort."""

    def __init__(self, route_service_url:str):
        self.route_service_url = route_service_url

    @catch_unavailable_service("Routes")
    def find_route_by_flight_id(self, flightId:str) -> Optional[Route]:
        response: Response = requests.get(
            f"{self.post_service_url}/{flightId}",
        )

        if response.status_code != 200:
            return None
        
        route_response = Route(**response.json())

        return route_response
    
    @catch_unavailable_service('Routes')
    def create_route(self, route_dto: RouteCreateInput):
        request_body = route_dto.model_dump()

        response: Response = requests.post(
            f"{self.route_service_url}",
            json=request_body,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 201:
            return None
        
        return CreatedRoute(**response.json())
    

    @catch_unavailable_service("Routes")
    def ping(self) -> None:
        response: Response = requests.get(f"{self.route_service_url}/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Routes service is not working")
    





class HTTPPostsClientAdapter(PostsPort):
    """Implementation of RoutesPort."""

    def __init__(self, post_service_url:str):
        self.post_service_url = post_service_url

    @catch_unavailable_service("Posts")
    def get_post_from_userid_route_id(self, user_id:str, route_id:str) -> Optional[List[Post]]:
        response: Response = requests.get(
            f"{self.post_service_url}",
            params={'route':route_id, 'owner':user_id}
        )

        if response.status_code != 200:
            return None

        try:
            post_data_list = response.json()
            # Check if the response is a list
            if not isinstance(post_data_list, list):
                # Handle cases where the endpoint might return a single object or an error
                return None
                
            return [Post(**post_data) for post_data in post_data_list]
        except (requests.exceptions.JSONDecodeError, KeyError, TypeError):
            # Handle cases where the JSON is malformed or keys are missing
            return None
    

    @catch_unavailable_service('Posts')
    def create_post(self, create_post_dto: CreatePost) -> Optional[CreatedPost]:
        request_body = create_post_dto.model_dump()

        response: Response = requests.post(
            f"{self.post_service_url}",
            json=request_body,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 201:
            return None
        
        return CreatedPost(**response.json())
    

    @catch_unavailable_service("Posts")
    def ping(self) -> None:
        response: Response = requests.get(f"{self.post_service_url}/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Posts service is not working")















"""
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
    #Adaptador HTTP para el servicio de usuarios.
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
    #Adaptador HTTP para el servicio de Rutas.
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
    #Adaptador HTTP para el servicio de Publicaciones.
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
        

    async def create_post(self, create_post_dto: CreatePost) -> CreatePostResponse:
        try:
            json_data = create_post_dto.model_dump_json()
            resp = await self._request("POST", "/posts", data=json_data, headers={"Content-Type": "application/json"})

            if resp.status_code == 201:  # 201 Created is the standard for successful creation
                return CreatePostResponse(**resp.json())
            
            # Handle specific error cases from the service
            elif resp.status_code == 400:
                raise ValidationError("Los datos de entrada no son válidos.")
            
            elif resp.status_code == 412:
                raise ConflictError("Trayecto ya existe o fechas son incorrectas.")
            
        except Exception:
            raise ServiceCommunicationError(f"routes. Status code: {resp.status_code}")
"""