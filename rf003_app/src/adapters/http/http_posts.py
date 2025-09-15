from functools import wraps
from requests.exceptions import RequestException
import httpx ## CAMBIO: Importamos httpx en lugar de requests
from typing import List, Optional

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort, RouteCreateInput
from src.domain.models.models import User, Route, Post, CreatedRoute, CreatedPost, CreatePost
from src.errors import ServiceCommunicationError

def catch_unavailable_service(service_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs): 
            try:
                return await func(*args, **kwargs) 
            except (httpx.RequestError, httpx.ConnectError, httpx.TimeoutException): 
                raise ServiceCommunicationError(f'{service_name} service is not available')
        return wrapper
    return decorator

class HTTPClientBase:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def close(self):
        await self.client.aclose()

# Users
class HTTPUsersClientAdapter(HTTPClientBase, UsersPort):
    "Implementation of UsersPort."

    def __init__(self, user_service_url: str):
        super().__init__(base_url=user_service_url)

    @catch_unavailable_service("Users")
    async def get_user_from_token(self, token:str) -> Optional[User]: 
        "Validate token and get user. Return None if token invalid"
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

# Routes
class HTTPRoutesClientAdapter(HTTPClientBase, RoutesPort):
    """Implementation of RoutesPort."""

    def __init__(self, route_service_url:str):
        super().__init__(base_url=route_service_url)

    @catch_unavailable_service("Routes")
    async def find_route_by_flight_id(self, flightId:str) -> Optional[Route]:
        params = {"flight": flightId}
        response = await self.client.get("/routes", params=params)
        
        if response.status_code != 200:
            return None
        
        items = response.json() or []
        items = [r for r in items if r.get("flightId") == flightId]

        return Route(**items[0]) if items else None
    
    @catch_unavailable_service('Routes')
    async def create_route(self, route_dto: RouteCreateInput) -> Optional[CreatedRoute]:
        response = await self.client.post("/routes", json=route_dto.model_dump())

        if response.status_code != 201:
            return None
        return CreatedRoute(**response.json())
    
    @catch_unavailable_service("Routes")
    async def ping(self) -> None:
        response = await self.client.get("/routes/ping")
        if response.status_code != 200:
            raise ServiceCommunicationError("Routes service is not working")

# Posts
class HTTPPostsClientAdapter(HTTPClientBase, PostsPort):
    """Implementation of PostsPort."""

    def __init__(self, post_service_url:str):
        super().__init__(base_url=post_service_url)

    async def get_post_from_userid_route_id(self, user_id:str, route_id:str) -> Optional[List[Post]]: 
        params = {'route': route_id, 'owner': user_id}
        response = await self.client.get("/posts", params=params) 
        if response.status_code != 200:
            return [] 

        # Solo si el status es 200, procesa el JSON
        response_data = response.json()
        if not response_data:
            return [] 
        
        return [Post(**post_data) for post_data in response_data]
    
    @catch_unavailable_service('Posts')
    async def create_post(self, create_post_dto: CreatePost) -> Optional[CreatedPost]: 
        payload = create_post_dto.model_dump(mode="json")
        response = await self.client.post("/posts", json=payload) 

        if response.status_code != 201:
            return None
        return CreatedPost(**response.json())

    @catch_unavailable_service("Posts")
    async def ping(self) -> None: 
        response = await self.client.get("/posts/ping") 
        if response.status_code != 200:
            raise ServiceCommunicationError("Posts service is not working")