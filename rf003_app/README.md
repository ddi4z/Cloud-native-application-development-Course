# rf003 – Orquestador de Creación de Publicaciones

Este proyecto es una aplicación FastAPI que implementa el patrón de orquestación y sigue los
principios de la arquitectura hexagonal. Su única responsabilidad es cumplir con el
requerimiento RF-003: crear una publicación para un usuario autenticado.

Como orquestador, este servicio es sin estado (stateless) y no tiene su propia base de datos. En su lugar, se comunica a través de clientes HTTP con los siguientes microservicios:
● **users_app** : Para autenticar y autorizar al usuario a partir de un token.
● **routes_app** : Para verificar si el trayecto de la publicación ya existe y, si no, crearlo.
● **posts_app** : Para verificar que el usuario no tenga ya una publicación para el mismo
trayecto y para crear la nueva publicación.

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
rf003_app/
├── src/
│ └── rf003_app/
│ ├── adapters/ # Implementaciones de los puertos (Clientes HTTP)
│ │ └── http/
│ ├── domain/ # Lógica de orquestación y modelos de dominio
│ │ ├── models/ # Modelos de datos para comunicación interna
│ │ ├── ports/ # Interfaces (contratos) para los clientes HTTP
│ │ └── use_cases/ # Lógica que orquesta las llamadas a los servicios
│ ├── entrypoints/ # Puntos de entrada de la aplicación
│ │ └── api/ # API REST con FastAPI (routers y main)
│ ├── assembly.py # Inyección de dependencias de los clientes
│ └── errors.py # Excepciones personalizadas
├── tests/ # Pruebas unitarias y de integración
├── Dockerfile # Definición de la imagen Docker
├── pyproject.toml # Dependencias y configuración de Poetry
└── README.md # Esta documentación
```

### Dominio

Contiene el núcleo de la lógica de negocio.

* **/domain/models** : Define los modelos que el orquestador usa para comunicarse con
otros servicios y para construir su respuesta.

``` python
# src/rf003_app/domain/models/models.py

from pydantic import BaseModel
from typing import List, Optional

# Modelo de entrada del usuario
class UserInput(BaseModel):
    flightId: str
    expireAt: str
    plannedStartDate: str
    plannedEndDate: str
    origin: RouteOrigin
    destiny: RouteDestiny
    bagCost: int
# Modelo para crear un trayecto en routes_app
class RouteCreateInput(BaseModel):
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    # ... otros campos 
# Modelo para crear una publicación en posts_app
class CreatePost(BaseModel):
    id: str # Corresponde al routeId
    expireAt: str
    userId: str
# Modelo de la respuesta final de la API
class PublicationResponse(BaseModel):
    data: PublicationResponseData
    msg: str = 'Publicación creada exitosamente'
```

* **/domain/ports** : Define las interfaces que la lógica de negocio utiliza para interactuar con servicios externos (users, posts, routes).

``` python
# src/rf003_app/domain/ports/rf003_port.py
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models.models import User, Route, Post, CreatedRoute,
RouteCreateInput, CreatePost
    class UsersPort(ABC):
        @abstractmethod
        def get_user_from_token(self, token: str) -> Optional[User]:
        raise NotImplementedError
    class RoutesPort(ABC):
        @abstractmethod
        def find_route_by_flight_id(self, flightId: str) -> Optional[Route]:
            raise NotImplementedError
        @abstractmethod
        def create_route(self, route_dto: RouteCreateInput) -> Optional[CreatedRoute]:
            raise NotImplementedError
        class PostsPort(ABC):
        @abstractmethod
        def get_post_from_userid_route_id(self, user_id: str, route_id: str) ->
            Optional[List[Post]]:
            raise NotImplementedError
        @abstractmethod
        def create_post(self, create_post_dto: CreatePost) -> Optional[CreatedPost]:
            raise NotImplementedError
```

* **/domain/use_cases** : Contiene la lógica de aplicación que orquesta los modelos y
puertos para cumplir con los requisitos funcionales.

``` python
# src/rf003_app/domain/use_cases/create_post.py
from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort
from src.errors import InvalidTokenError, ConflictError
    class CreatePostUseCase(BaseUseCase):
        def __init__(
        self,
        users_client: UsersPort,
        routes_client: RoutesPort,
        posts_client: PostsPort
    )
    # Otros casos de uso ... 
```

### Adaptadores

Contiene las implementaciones concretas de los puertos. Para este servicio, son clientes
HTTP que se comunican con las APIs de otros microservicios usando **requests** o **httpx**.

``` python
# src/rf003_app/adapters/http/http_posts.py
import requests
from src.domain.ports.rf003_port import UsersPort
from src.domain.models.models import User
    class HTTPUsersClientAdapter(UsersPort):
        def __init__(self, user_service_url: str):
            self.user_service_url = user_service_url
    def get_user_from_token(self, token: str) -> Optional[User]:
        response = requests.get(
        f"{self.user_service_url}/me",
        headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code != 200:
            return None
        return User(**response.json())
```

### Entrypoints

Define la API REST con **FastAPI** que expone la funcionalidad del orquestador.

``` python
# src/rf003_app/entrypoints/api/routers/router.py
from fastapi import APIRouter, Depends, Header, HTTPException
from src.assembly import build_create_post_use_case
# ... Imports adicionales
router = APIRouter(prefix='/rf003')
@router.post("/posts", response_model=PublicationResponse, status_code=201)
def create_post(
    input_dto: UserInput,
    token: str = Depends(get_current_token),
    use_case: BaseUseCase = Depends(build_create_post_use_case),
    ):
    """Crea una nueva publicación."""
    try:
    # Lógica para llamar al caso de uso y construir la respuesta
    created_post, ... = use_case.execute(token=token, input_dto=input_dto)
    # ... construir objeto de respuesta


    return api_answer
        except InvalidTokenError as e:
    raise HTTPException(status_code=401, detail=str(e))
        except ConflictError as e:
    raise HTTPException(status_code=412, detail=str(e))
# ... otros manejadores de excepciones
```

## Ejecución de la Aplicación

### Prerrequisitos

``` bash
● Python 3.11+
● Poetry
● Docker
● Minikube / Kubernetes
```

#### Instalar dependencias

Desde la carpeta rf003_app:

``` bash
poetry install
```

#### Ejecutar la Aplicación Localmente

Exporta las variables de entorno y levanta el servidor:

``` bash
export USERS_SERVICE_URL=http://localhost:
export ROUTES_SERVICE_URL=http://localhost:
export POSTS_SERVICE_URL=http://localhost:
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8003
```

La API estará disponible en [http://localhost:8003.](http://localhost:8003.)

## Ejecutar en Docker

### 1. Construir la imagen

``` bash
docker build -t rf003-app:v1.0..
```

### 2. Ejecutar el contenedor

Pasa **todas** las variables de entorno requeridas:

``` bash
docker run --rm -p 8003:8003 \
-e USERS_SERVICE_URL="http://users-app-service" \
-e ROUTES_SERVICE_URL="http://routes-app-service" \
-e POSTS_SERVICE_URL="http://posts-app-service" \
rf003-app:v1.0.
```

## Ejecutar en Minikube/Kubernetes

```bash
minikube image build -t rf003-app:v1.0.0 .
eval $(minikube docker-env)
docker build -t rf003-app:v1.0.0 .
kubectl apply -f k8s/local/rf003_app.yaml
```

## Endpoints de la API

| Método | Ruta                     | Descripción                                                             | Auth |
|-------:|--------------------------|-------------------------------------------------------------------------|:----:|
| GET    | `/rf003/ping`            | Verifica el estado de salud del servicio.                               |  –   |
| GET    | `/rf003/posts/{post_id}` | Crea una nueva publicación para elusuario.     | ✅   |

## Autor

Manuel Estevez Breton – <me.estevez-breton10@uniandes.edu.co>
