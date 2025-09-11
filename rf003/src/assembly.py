import os
from src.domain.use_cases.create_post import CreatePostUseCase
from src.adapters.http.http_posts import (
    HTTPUsersClientAdapter,
    HTTPPostsClientAdapter,
    HTTPRoutesClientAdapter
)


# Instanciamiento de los clientes HTTP reales para comunicarse con los otros microservicios.
users_client = HTTPUsersClientAdapter(base_url=os.getenv("USERS_SERVICE_URL"))
posts_client = HTTPPostsClientAdapter(base_url=os.getenv("POSTS_SERVICE_URL"))
routes_client = HTTPRoutesClientAdapter(base_url=os.getenv("ROUTES_SERVICE_URL"))


def build_get_post_sorted_by_score_use_case() -> CreatePostUseCase:
    """
    Construye el caso de uso para obtener una publicación completa,
    inyectando todas las dependencias (clientes).
    """
    return CreatePostUseCase(
        users_client=users_client,
        posts_client=posts_client,
        routes_client=routes_client
    )

