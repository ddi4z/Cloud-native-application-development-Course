import os
from importlib import import_module
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_post import CreatePostUseCase
from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort

services = ['USERS', 'ROUTES', 'POSTS']
url_services = {}
for service in services:
    env_key = f"{service}_SERVICE_URL"
    if env_key not in os.environ:
        raise EnvironmentError(f"{env_key} environment variable not set")
    url_services[service] = os.environ[env_key]

def _load_http_adapters_module():
    """
    Carga perezosa de src.adapters.http.http_posts y valida símbolos.
    Si algo falta, levanta ImportError indicando qué símbolos tiene el módulo.
    """
    modname = "src.adapters.http.http_posts"
    try:
        mod = import_module(modname)
    except Exception as e:
        raise ImportError(f"No pude importar '{modname}': {e}")

    required = ("HTTPUsersClientAdapter", "HTTPPostsClientAdapter", "HTTPRoutesClientAdapter")
    missing = [name for name in required if not hasattr(mod, name)]
    if missing:
        exported = ", ".join(sorted(dir(mod)))
        raise ImportError(
            f"El módulo '{modname}' no define: {', '.join(missing)}. "
            f"Sí exporta: {exported}"
        )
    return mod

def build_create_post_use_case() -> BaseUseCase:
    """
    Construye el caso de uso para crear publicación,
    inyectando clientes HTTP con lazy import para evitar ciclos.
    """
    mod = _load_http_adapters_module()

    HTTPUsersClientAdapter  = getattr(mod, "HTTPUsersClientAdapter")
    HTTPPostsClientAdapter  = getattr(mod, "HTTPPostsClientAdapter")
    HTTPRoutesClientAdapter = getattr(mod, "HTTPRoutesClientAdapter")

    users_adapter: UsersPort   = HTTPUsersClientAdapter(url_services['USERS'])
    routes_adapter: RoutesPort = HTTPRoutesClientAdapter(url_services['ROUTES'])
    posts_adapter: PostsPort   = HTTPPostsClientAdapter(url_services['POSTS'])

    return CreatePostUseCase(
        users_client=users_adapter,
        routes_client=routes_adapter,
        posts_client=posts_adapter
    )
