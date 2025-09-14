# rf005 – Orquestador de Publicaciones

Este proyecto es una aplicación FastAPI que implementa el patrón de orquestación y sigue los principios de la arquitectura hexagonal. Su única responsabilidad es cumplir con el requerimiento RF-005: consultar una publicación, obtener sus ofertas, calcular la utilidad de cada una y devolver la información completa con las ofertas ordenadas de mayor a menor utilidad.

Como orquestador, este servicio es sin estado (stateless) y no tiene su propia base de datos. En su lugar, se comunica a través de clientes HTTP con los siguientes microservicios:

* users_app: Para autenticar y autorizar al usuario.
* posts_app: Para obtener los datos de la publicación.
* routes_app: Para obtener la información del trayecto asociado.
* offers_app: Para obtener la lista de ofertas de la publicación.
* scores_app: Para calcular la utilidad (score) de cada oferta.

## Índice

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Ejecución de la Aplicación](#ejecución-de-la-aplicación)
3. [Ejecutar en Docker](#ejecutar-en-docker)
4. [Ejecutar en Minikube/Kubernetes](#ejecutar-en-minikubekubernetes)
5. [Endpoints de la API](#endpoints-de-la-api)
6. [Autor](#autor)

## Estructura del Proyecto

La aplicación sigue los principios de la arquitectura hexagonal para separar la lógica de negocio de la infraestructura de comunicación.

``` bash
rf005/
├── src/
│   └── rf005/
│       ├── adapters/               # Implementaciones de los puertos (Clientes HTTP)
│       │   └── http/               # Clientes HTTP para otros microservicios
│       ├── domain/                 # Lógica de orquestación y modelos de dominio
│       │   ├── models/             # Modelos de datos para respuestas internas y externas
│       │   ├── ports/              # Interfaces (contratos) para los clientes HTTP
│       │   └── use_cases/          # Lógica que orquesta las llamadas a los servicios
│       ├── entrypoints/            # Puntos de entrada de la aplicación
│       │   └── api/                # API REST con FastAPI (routers y main)
│       ├── assembly.py             # Inyección de dependencias de los clientes
│       └── errors.py               # Excepciones personalizadas
├── tests/                          # Pruebas unitarias y de integración
├── Dockerfile                      # Definición de la imagen Docker
├── pyproject.toml                  # Dependencias y configuración de Poetry
└── README.md                       # Esta documentación
```

### Dominio

Contiene el núcleo de la lógica de negocio.

* **/domain/models**: Define los modelos que el orquestador usa para construir la respuesta final (inputs de otros servicios y el output consolidado).

    ```python
    # src/rf005/domain/models/models.py
    from __future__ import annotations

    from datetime import datetime
    from typing import List, Optional
    from pydantic import BaseModel, Field

    class User(BaseModel):
        id: str
        email: Optional[str] = None
        segment: Optional[str] = None

    class RouteDetails(BaseModel):
        id: str
        sourceAirportCode: str = Field(..., min_length=3, max_length=3)
        destinyAirportCode: str = Field(..., min_length=3, max_length=3)
        distanceMeters: Optional[int] = None
        plannedStartDate: Optional[datetime] = None
        plannedEndDate: Optional[datetime] = None

    class OfferDetails(BaseModel):
        id: str
        userId: str
        score: Optional[float] = None
        price: Optional[float] = None
        discountPct: Optional[float] = None
        # ... otros campos de la oferta

    class PostDetails(BaseModel):
        id: str
        routeId: str
        offerIds: List[str] = []

    class PublicationResponseData(BaseModel):
        id: str
        route: RouteDetails
        offers: List[OfferDetails]
        # ... otros campos de la publicación

    class PublicationResponse(BaseModel):
        data: PublicationResponseData
    ```

* **/domain/ports**: Define las interfaces que la lógica de negocio utiliza para interactuar con servicios externos (users, posts, routes, offers, scores). Esto desacopla la lógica del detalle de transporte/cliente HTTP.

    ```python
    # src/rf005/domain/ports/ports.py
    from __future__ import annotations

    from abc import ABC, abstractmethod
    from typing import List, Optional

    from rf005.domain.models.models import (
        User, PostDetails, RouteDetails, OfferDetails
    )

    class APIClientPort(ABC):
        """Puerto base para clientes externos (HTTP, gRPC, etc.)."""
        ...

    class UsersClientPort(APIClientPort):
        @abstractmethod
        async def get_user_from_token(self, token: str) -> User:
            """Obtiene el usuario autenticado a partir del token."""
            raise NotImplementedError

    class PostsClientPort(APIClientPort):
        @abstractmethod
        async def get_post(self, post_id: str) -> PostDetails:
            raise NotImplementedError

    class RoutesClientPort(APIClientPort):
        @abstractmethod
        async def get_route(self, route_id: str) -> RouteDetails:
            raise NotImplementedError

    class OffersClientPort(APIClientPort):
        @abstractmethod
        async def get_offers(self, offer_ids: List[str]) -> List[OfferDetails]:
            raise NotImplementedError

    class ScoresClientPort(APIClientPort):
        @abstractmethod
        async def get_offer_score(
            self, user_id: str, offer_id: str
        ) -> Optional[float]:
            """Retorna el score calculado para (user, offer) si existe."""
            raise NotImplementedError
    ```

* **/domain/use_cases**: Contiene la lógica de aplicación que orquesta los modelos y puertos para cumplir con los requisitos funcionales.

    ```python
    # src/rf005/domain/use_cases/get_post_sorted_by_score_use_case.py
    from __future__ import annotations

    from typing import List

    from rf005.domain.models.models import PublicationResponse, PublicationResponseData, OfferDetails
    from rf005.domain.ports.ports import (
        UsersClientPort, PostsClientPort, RoutesClientPort, OffersClientPort, ScoresClientPort
    )

    class GetPostSortedByScoreUseCase:
        """Caso de uso para construir la publicación con ofertas ordenadas por score."""

        def __init__(
            self,
            users_client: UsersClientPort,
            posts_client: PostsClientPort,
            routes_client: RoutesClientPort,
            offers_client: OffersClientPort,
            scores_client: ScoresClientPort,
        ) -> None:
            self.users_client = users_client
            self.posts_client = posts_client
            self.routes_client = routes_client
            self.offers_client = offers_client
            self.scores_client = scores_client

        async def execute(self, *, post_id: str, token: str) -> PublicationResponse:
            # 1) Usuario autenticado
            user = await self.users_client.get_user_from_token(token)

            # 2) Post + route
            post = await self.posts_client.get_post(post_id)
            route = await self.routes_client.get_route(post.routeId)

            # 3) Ofertas
            offers: List[OfferDetails] = await self.offers_client.get_offers(post.offerIds)

            # 4) Scores (enriquecer ofertas con score del servicio de rf005/scores)
            #    Si no hay score, se mantiene None y se ordena al final.
            for offer in offers:
                offer.score = await self.scores_client.get_offer_score(user.id, offer.id)

            # 5) Ordenamiento por score (desc), manteniendo estabilidad para None
            offers_sorted = sorted(
                offers,
                key=lambda o: (-o.score if o.score is not None else float("inf"))
            )

            data = PublicationResponseData(
                id=post.id,
                route=route,
                offers=offers_sorted,
            )
            return PublicationResponse(data=data)
    ```

---

### Adaptadores

Contiene las implementaciones concretas de los puertos. Para este servicio, los adaptadores son clientes HTTP que se comunican con las APIs de los otros microservicios usando **httpx**.

```python
# src/rf005/adapters/http/users_client_adapter.py
import httpx
from rf005.domain.models.models import User
from rf005.domain.ports.ports import UsersClientPort

class HTTPUsersClientAdapter(UsersClientPort):
    def __init__(self, base_url: str, timeout_s: float = 5.0) -> None:
        self._base_url = base_url
        self._timeout = timeout_s

    async def get_user_from_token(self, token: str) -> User:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            resp = await client.get("/users/me", headers={"Authorization": token})
            resp.raise_for_status()
            return User.model_validate(resp.json())
```

#### Entrypoints

Define la API REST con **FastAPI** que expone la funcionalidad del orquestador.

```python
# src/rf005/entrypoints/api/routers/routers.py
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status

... Imports adicionales

router = APIRouter(prefix="/rf005", tags=["rf005"])

@router.get("/posts/{post_id}", response_model=PublicationResponse)
async def get_publication_details(
    post_id: str,
    authorization: Annotated[Optional[str], Header()] = None,
    use_case: GetPostSortedByScoreUseCase = Depends(build_get_post_sorted_by_score_use_case),
):
    """Retorna los detalles de una publicación con sus ofertas ordenadas por score."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )
    try:
        return await use_case.execute(post_id=post_id, token=authorization)
    except HTTPException:
        # Relevanta errores ya mapeados por FastAPI
        raise
    except Exception as exc:
        # Mapea fallas aguas arriba (clientes HTTP, timeouts, etc.)
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}")
```

### Ensamblaje (Assembly)

El archivo src/rf005/assembly.py se encarga de la inyección de dependencias. Aquí se instancian todos los clientes HTTP (HTTPUsersClientAdapter, HTTPPostsClientAdapter, etc.) y se inyectan en el caso de uso principal.

`src/rf005/assembly.py`

```python
# src/rf005/assembly.py
import os
from rf005.adapters.http.users_client_adapter import HTTPUsersClientAdapter
from rf005.adapters.http.posts_client_adapter import HTTPPostsClientAdapter
from rf005.adapters.http.routes_client_adapter import HTTPRoutesClientAdapter
from rf005.adapters.http.offers_client_adapter import HTTPOffersClientAdapter
from rf005.adapters.http.scores_client_adapter import HTTPScoresClientAdapter
from rf005.domain.use_cases.get_post_sorted_by_score_use_case import GetPostSortedByScoreUseCase

# 1) Config (con defaults útiles para k8s Services)
USERS_SERVICE_URL  = os.getenv("USERS_SERVICE_URL",  "http://users-app")
POSTS_SERVICE_URL  = os.getenv("POSTS_SERVICE_URL",  "http://posts-app")
ROUTES_SERVICE_URL = os.getenv("ROUTES_SERVICE_URL", "http://routes-app")
OFFERS_SERVICE_URL = os.getenv("OFFERS_SERVICE_URL", "http://offers-app")
SCORES_SERVICE_URL = os.getenv("SCORES_SERVICE_URL", "http://scores-app")

# 2) Adaptadores (singletons a nivel de módulo)
_users  = HTTPUsersClientAdapter(base_url=USERS_SERVICE_URL)
_posts  = HTTPPostsClientAdapter(base_url=POSTS_SERVICE_URL)
_routes = HTTPRoutesClientAdapter(base_url=ROUTES_SERVICE_URL)
_offers = HTTPOffersClientAdapter(base_url=OFFERS_SERVICE_URL)
_scores = HTTPScoresClientAdapter(base_url=SCORES_SERVICE_URL)

# 3) Factory del caso de uso principal
def build_get_post_sorted_by_score_use_case() -> GetPostSortedByScoreUseCase:
    return GetPostSortedByScoreUseCase(
        users_client=_users,
        posts_client=_posts,
        routes_client=_routes,
        offers_client=_offers,
        scores_client=_scores,
    )
```

### Ejecución de la Aplicación

Breve guía para correr **rf005** en local, Docker y Minikube/Kubernetes.

#### 1) Prerrequisitos

* Python 3.11+
* Poetry
* Docker
* Minikube / Kubernetes

#### 2) Instalar dependencias

Desde la carpeta `rf005`:

```bash
poetry install
```

### 3) Ejecutar la Aplicación Localmente

Exporta variables de entorno y levanta el servidor:

```bash
export USERS_SERVICE_URL=http://localhost:8080
export POSTS_SERVICE_URL=http://localhost:8081
# export ROUTES_SERVICE_URL=...
# export OFFERS_SERVICE_URL=...
# export SCORES_SERVICE_URL=...
poetry run uvicorn rf005.entrypoints.api.main:app --host 0.0.0.0 --port 8005
```

La API estará disponible en <http://localhost:8005>.

### Ejecutar en Docker

#### 1. Construir la imagen

```bash
docker build -t rf005-app:v1.0.0 .
```

**2) Ejecutar el contenedor**  
Pasa **todas** las variables de entorno requeridas:

```bash
docker run --rm -p 8005:8005 \
  -e USERS_SERVICE_URL="http://users-app" \
  -e POSTS_SERVICE_URL="http://posts-app" \
  -e ROUTES_SERVICE_URL="http://routes-app" \
  -e OFFERS_SERVICE_URL="http://offers-app" \
  -e SCORES_SERVICE_URL="http://scores-app" \
  rf005-app:v1.0.0
```

### Ejecutar en Minikube/Kubernetes

#### 1) Construir la imagen dentro de Minikube

```bash
minikube image build -t rf005-app:v1.0.0 .
eval $(minikube docker-env)
docker build -t rf005-app:v1.0.0 .
```

**2. Desplegar el manifiesto de Kubernetes:**
El archivo rf005_app.yaml debe tener definidas las variables de entorno apuntando a los nombres de servicio correctos dentro del clúster (ej. <http://users-app-service>).

```bash
kubectl apply -f k8s/local/rf005_app.yaml
```

**3. Exponer y acceder al servicio:**

```bash
kubectl port-forward service/rf005-app-service 8005:80
```

### Endpoints de la API

| Método | Ruta                     | Descripción                                                             | Auth |
|-------:|--------------------------|-------------------------------------------------------------------------|:----:|
| GET    | `/rf005/ping`            | Verifica el estado de salud del servicio.                               |  –   |
| GET    | `/rf005/posts/{post_id}` | Devuelve la publicación con ofertas ordenadas por utilidad (score).     | ✅   |

> **Auth requerida** (`/rf005/posts/{post_id}`): header `Authorization: <token>`

#### Ejemplo

#### Ping

```bash
curl -X GET http://localhost:8005/rf005/ping
```

## Autor

Jorge Paternina – [j.paterninam@uniandes.edu.co](mailto:j.paterninam@uniandes.edu.co)
