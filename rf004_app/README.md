# rf004 – Orquestador de Creación de Ofertas

Este proyecto es una aplicación FastAPI que implementa el patrón de orquestación y sigue los principios de la arquitectura hexagonal. Su única responsabilidad es cumplir con el requerimiento RF-004: crear una oferta sobre una publicación existente para un usuario autenticado.

Como orquestador, este servicio es sin estado (stateless) y no tiene su propia base de datos. En su lugar, se comunica a través de clientes HTTP con los siguientes microservicios:
● **users_app** : Para autenticar y autorizar al usuario a partir de un token.
● **posts_app** : Para validar que la publicación a la que se oferta existe, no ha expirado y
no pertenece al mismo usuario.
● **routes_app** : Para obtener el costo de la maleta ( bagCost ) del trayecto asociado a la publicación.
● **offers_app** : Para persistir la nueva oferta creada.
● **scores_app** : Para calcular y persistir la utilidad (score) de la nueva oferta.

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
rf004_app/
├── src/
│ └── rf004_app/
│ ├── adapters/ # Clientes HTTP para otros microservicios
│ ├── domain/ # Lógica de orquestación y modelos
│ │ ├── models/ # Modelos de datos para comunicación
│ │ ├── ports/ # Interfaces para los clientes HTTP
│ │ └── use_cases/ # Lógica de orquestación
│ ├── entrypoints/ # Puntos de entrada (API REST)
│ │ └── api/
│ ├── assembly.py # Inyección de dependencias
│ └── errors.py # Excepciones personalizadas
├── tests/
├── Dockerfile
├── pyproject.toml
└── README.md # Esta documentación
```

### Dominio

Contiene el núcleo de la lógica de negocio.
* **/domain/models** : Define los modelos que el orquestador usa para comunicarse con otros servicios.

``` python
# src/rf004_app/domain/models/offer.py
from pydantic import BaseModel
from enum import Enum
  class OfferSize(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
  class Offer(BaseModel):
  """Modelo de entrada para una oferta."""
    description: str
    size: OfferSize
    fragile: bool
    offer: int
  class CreatedOffer(BaseModel):
  """Modelo de respuesta del servicio de ofertas."""
    id: str
    userId: str
    createdAt: str
```

* **/domain/ports** : Define las interfaces que la lógica de negocio utiliza para interactuar con servicios externos.

``` python
# src/rf004_app/domain/ports/user_validation_port.py
from abc import abstractmethod
from src.domain.models.user import User
class UserValidationPort(HttpRequest):
@abstractmethod
def validate_token_and_get_user(self, token: str) -> Optional[User]:
raise NotImplementedError

# src/rf004_app/domain/ports/post_validation_port.py
from src.domain.models.post import Post
class PostValidationPort(HttpRequest):
@abstractmethod
def validate_and_get_post(self, postId: str) -> Optional[Post]:
raise NotImplementedError
# ... y así para cada puerto (CreateOfferPort, ScoreCalculationPort, etc.)
```

* **/domain/use_cases** : Contiene la lógica de aplicación que orquesta los servicios para crear una oferta.

``` python
# src/rf004_app/domain/use_cases/create_offer_use_case.py
from src.errors import UnauthorizedError, PostNotFoundError, OfferOnOwnPostError,
PostExpiredError
  class CreateOfferUseCase(BaseUseCase):
  # ... __init__ con todos los clientes inyectados
  def execute(self, auth_token: str, post_id: str, offer: Offer) -> CreatedOffer:
    # 1. Validar usuario
    user = self.user_validation.validate_token_and_get_user(token=auth_token)
    if user is None:
      raise UnauthorizedError("Usuario no autorizado")
    # 2. Validar publicación
    post = self.post_validation.validate_and_get_post(postId=post_id)
    if post is None:
      raise PostNotFoundError(f"Publicación con id {post_id} no encontrada")
    if post.userId == user.id:
      raise OfferOnOwnPostError("Usuario no puede ofertar en su propia publicación")
    if datetime.fromisoformat(post.expireAt) < datetime.now(timezone.utc):
      raise PostExpiredError("La publicación ha expirado")
    # 3. Crear la oferta en offers_app
    created_offer = self.create_offer.create_offer(offer, userId=user.id, postId=post_id)
    # 4. Obtener bagCost de routes_app
    bagCost = self.find_bagcost.get_bagcost(post.routeId)
    # 5. Calcular y guardar score en scores_app
    score_payload = Score(
    offer_id=created_offer.id,
    size=offer.size,
    baggage_value=bagCost if bagCost is not None else 0,
    amount_offered=offer.offer,
    )
    self.score_calculation.calculate_score(score_payload)
    return created_offer
```

### Adaptadores

Son clientes HTTP que implementan los puertos para comunicarse con los otros microservicios.

``` python
# src/rf004_app/adapters/post_validation_adapter.py
import requests
from src.domain.ports.post_validation_port import PostValidationPort
from src.domain.models.post import Post
class PostValidationAdapter(PostValidationPort):
  def __init__(self, post_service_url: str):
    self.post_service_url = post_service_url
  def validate_and_get_post(self, postId: str) -> Optional[Post]:
    response = requests.get(f"{self.post_service_url}/{postId}")
    if response.status_code != 200:
      return None
    return Post(**response.json())
```

### Entrypoints

Define la API REST con **FastAPI** que expone la funcionalidad del orquestador.

``` python
# src/rf004_app/entrypoints/api/routers/offer_router.py
from fastapi import APIRouter, Depends, HTTPException
from src.assembly import build_create_offer_use_case
from src.entrypoints.api.dtos.offer_info_dto import OfferInfoDto
router = APIRouter(prefix="/rf004")
@router.post("/posts/{postId}/offers", response_model=OfferWrapperDto, status_code=201)
  def create_offer(
    offer: OfferInfoDto,
    postId: str,
    token: str = Depends(get_current_token),
    use_case: BaseUseCase = Depends(build_create_offer_use_case),
    ):
    """Crea una nueva oferta en una publicación."""
    try:
      created_offer = use_case.execute(
      auth_token=token,
      post_id=postId,
      offer=offer,
      )
    # ... construir respuesta
      return OfferWrapperDto(data=created_offer_dto)
    except PostNotFoundError as e:
      raise HTTPException(status_code=404, detail=str(e))
    except (OfferOnOwnPostError, PostExpiredError) as e:
      raise HTTPException(status_code=412, detail=str(e))
# ... otros manejadores de excepciones
```

## Ejecución de la Aplicación

### **Prerrequisitos**

* Python 3.11+
* Poetry
* Docker
* Minikube / Kubernetes

### **Instalar dependencias**

Desde la carpeta rf004_app :

``` bash
poetry install
```

### **Ejecutar la Aplicación Localmente**

``` bash
export USERS_SERVICE_URL=http://localhost:
export POSTS_SERVICE_URL=http://localhost:
export ROUTES_SERVICE_URL=http://localhost:
export OFFERS_SERVICE_URL=http://localhost:
export SCORES_SERVICE_URL=http://localhost:
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8004
```

La API estará disponible en [http://localhost:](http://localhost:).

## Ejecutar en Docker

``` bash
docker build -t rf004-app:v1.0..
docker run --rm -p 8004:8004 \
-e USERS_SERVICE_URL="http://users-app-service" \
-e POSTS_SERVICE_URL="http://posts-app-service" \
-e ROUTES_SERVICE_URL="http://routes-app-service" \
-e OFFERS_SERVICE_URL="http://offers-app-service" \
-e SCORES_SERVICE_URL="http://scores-app-service" \
rf004-app:v1.0.
```

## Ejecutar en Minikube/Kubernetes

Aplica un manifiesto de Kubernetes similar al de rf005 , asegurándote de que el nombre de la imagen, el puerto y las 5 variables de entorno de servicio sean correctas.

```bash
minikube image build -t rf004-app:v1.0.0 .
eval $(minikube docker-env)
docker build -t rf004-app:v1.0.0 .
kubectl apply -f k8s/local/rf004_app.yaml
kubectl port-forward service/rf004-app-service 800x:80
```

## Endpoints de la API

| Método | Ruta                     | Descripción                                                             | Auth |
|-------:|--------------------------|-------------------------------------------------------------------------|:----:|
| GET    | `/rf004/ping`            | Verifica el estado de salud del servicio.                               |  –   |
| GET    | `/rf004/posts/{post_id}/offers` | Crea una nueva oferta en una publicación    | ✅   |

## Autor

Javier Barrera - [js.barrerat1@uniandes.edu.co](mailto:js.barrerat1@uniandes.edu.co)
