import os
from .domain.use_cases.get_post_sorted_by_score_use_case import GetPostSortedByScoreUseCase
from .adapters.http.http_clients import (
    HTTPUsersClientAdapter,
    HTTPPostsClientAdapter,
    HTTPRoutesClientAdapter,
    HTTPOffersClientAdapter,
)
from .adapters.memory.mock_clients import MockScoreClientAdapter

# Instanciación de los clientes HTTP reales para comunicarse con los otros microservicios.
users_client = HTTPUsersClientAdapter(base_url=os.getenv("USERS_SERVICE_URL"))
posts_client = HTTPPostsClientAdapter(base_url=os.getenv("POSTS_SERVICE_URL"))
routes_client = HTTPRoutesClientAdapter(base_url=os.getenv("ROUTES_SERVICE_URL"))
offers_client = HTTPOffersClientAdapter(base_url=os.getenv("OFFERS_SERVICE_URL"))

# Instanciación del cliente mock para el servicio de score, ya que aún no está desarrollado.
score_client = MockScoreClientAdapter()

def build_get_post_sorted_by_score_use_case() -> GetPostSortedByScoreUseCase:
    """
    Construye el caso de uso para obtener una publicación completa,
    inyectando todas las dependencias (clientes).
    """
    return GetPostSortedByScoreUseCase(
        users_client=users_client,
        posts_client=posts_client,
        routes_client=routes_client,
        offers_client=offers_client,
        score_client=score_client,
    )