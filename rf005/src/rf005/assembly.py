import os
from .domain.use_cases.get_post_sorted_by_score_use_case import GetPostSortedByScoreUseCase

# Revisa una variable de entorno para decidir qué adaptadores usar.
# Para producción/staging, el valor sería "production".
# Para pruebas locales con mocks, podría ser "test".
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

if ENVIRONMENT == "test":
    # En el entorno de prueba, usamos los clientes mock que están en memoria y no hacen llamadas HTTP reales.
    from .adapters.memory.mock_clients import (
        InMemoryUsersClientAdapter,
        InMemoryPostsClientAdapter,
        InMemoryRoutesClientAdapter,
        InMemoryOffersClientAdapter,
        MockScoreClientAdapter,
    )
    users_client = InMemoryUsersClientAdapter()
    posts_client = InMemoryPostsClientAdapter()
    routes_client = InMemoryRoutesClientAdapter()
    offers_client = InMemoryOffersClientAdapter()
    score_client = MockScoreClientAdapter()
else:
    # En un entorno de producción, usamos los clientes HTTP reales.
    from .adapters.http.http_clients import (
        HTTPUsersClientAdapter,
        HTTPPostsClientAdapter,
        HTTPRoutesClientAdapter,
        HTTPOffersClientAdapter,
    )
    # El servicio de Score siempre es un mock por ahora. 
    from .adapters.memory.mock_clients import MockScoreClientAdapter
    
    users_client = HTTPUsersClientAdapter()
    posts_client = HTTPPostsClientAdapter()
    routes_client = HTTPRoutesClientAdapter()
    offers_client = HTTPOffersClientAdapter()
    score_client = MockScoreClientAdapter()

def build_get_post_sorted_by_score_use_case() -> GetPostSortedByScoreUseCase:
    """
    Construye el caso de uso con sus dependencias concretas.
    Las dependencias cambian según la variable de entorno ENVIRONMENT.
    """
    return GetPostSortedByScoreUseCase(
        users_client=users_client,
        posts_client=posts_client,
        routes_client=routes_client,
        offers_client=offers_client,
        score_client=score_client,
    )