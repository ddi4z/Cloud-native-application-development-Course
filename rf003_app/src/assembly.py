import os
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_post import CreatePostUseCase

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort

from src.adapters.http.http_posts import HTTPUsersClientAdapter, HTTPPostsClientAdapter, HTTPRoutesClientAdapter


services = ['USERS', 'ROUTES', 'POSTS']
url_services = {}

for service in services:
    service_name = f"{service}_SERVICE_URL"
    if service_name not in os.environ:
        raise EnvironmentError(f"{service}_SERVICE_URL environment variable not set")
    
    url_services[service] = os.environ[service_name]


    users_adapter: UsersPort = HTTPUsersClientAdapter(url_services['USERS'])
    routes_adapter: RoutesPort = HTTPRoutesClientAdapter(url_services['ROUTES'])
    posts_adapter: PostsPort = HTTPPostsClientAdapter(url_services['POSTS'])


def build_create_post_use_case() -> BaseUseCase:
    """
    Construye el caso de uso para obtener una publicación completa,
    inyectando todas las dependencias (clientes).
    """
    return CreatePostUseCase(
        users_client=users_adapter,
        routes_client=routes_adapter,
        posts_client=posts_adapter
    )
