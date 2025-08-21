# post\_app – Servicio de Posts

Este proyecto es una **aplicación FastAPI** que implementa arquitectura hexagonal (puertos y adaptadores) para gestionar la entidad **Post**. La app puede ejecutarse localmente, en **Docker** y en **Kubernetes/Minikube**.

---

## Tabla de contenido

* [post\_app – Servicio de Posts](#post_app--servicio-de-posts)

  * [Tabla de contenido](#tabla-de-contenido)
  * [Requisitos](#requisitos)
  * [Estructura del Proyecto](#estructura-del-proyecto)

    * [Carpeta src](#carpeta-src)
      * [Domain](#domain)
      * [Adapters](#adapters)
      * [Entrypoints](#entrypoints)
      * [Configuración y ensamble](#configuración-y-ensamble)
      * [Errores](#errores)
    * [Configuración](#configuración)

  * [Ejecución de la aplicación](#ejecución-de-la-aplicación)
    * [1. Instale las dependencias](#1-instale-las-dependencias)
    * [2. Ejecución](#2-ejecución)
  * [Ejecutar en Docker](#ejecutar-en-docker)
  * [Ejecutar en Minikube/Kubernetes](#ejecutar-en-minikubekubernetes)
  * [API Endpoints](#api-endpoints)
  
  * [Post Model](#post-model)

  * [Pruebas](#pruebas)
    * [Unitarias](#unitarias)
    * [Integración](#integración)
  
  * [Cómo contribuir](#cómo-contribuir)
  * [Licencia](#licencia)
  * [Autor](#autor)

---

## Requisitos

* Python **3.11**
* Poetry **2.1.1**
* Docker
* Postman (opcional pero recomendado)
* Minikube + kubectl (para Kubernetes)

---

## Estructura del Proyecto

```
.
├── src/
│   ├── domain/                # Capa de dominio
│   │   ├── models/            # Modelos de dominio (pydantic)
│   │   ├── ports/             # Puertos (interfaces)
│   │   └── use_cases/         # Casos de uso (lógica de aplicación)
│   ├── adapters/              # Implementaciones de puertos
│   │   └── database/          # Adaptador de base de datos (SQLAlchemy, etc.)
│   └── entrypoints/           # Puntos de entrada
│       └── api/               # Routers FastAPI
│           └── routers/
├── k8s/                       # Manifests de Kubernetes
├── tests/                     # Pruebas unitarias e integración
│   └── api/                   # Colecciones Postman/Newman
├── Dockerfile                 # Build multi-stage (rootless)
├── pyproject.toml             # Configuración de Poetry, linters y pytest
└── README.md                  # Este archivo
```

### Carpeta src

Esta carpeta contiene el código y la lógica de la aplicación que expone el API y orquesta integraciones.

#### Domain

Contiene el **corazón del negocio**: entidades, interfaces y casos de uso. Las entidades **no** dependen de frameworks ni de la base de datos.

* `/domain/models`: clases que representan las entidades del dominio (**Post**, etc.). Se usan modelos **pydantic** por validación y compatibilidad con FastAPI.

```python
# src/domain/models/post.py
class Post(BaseModel):
    """Post domain model."""
    id: UUID
    routeId: UUID = Field(description="Route identifier in UUID format")
    userId: UUID = Field(description="User Id of the user who owns the post")
    expireAt: datetime = Field(description="Date and time when post offer expires, in ISO format")
    createdAt: datetime = Field(description="Date and time when the post was created")
```

* `/domain/ports`: **interfaces** para integrar almacenamiento u otros servicios.

```python
# src/domain/ports/post_repository_port.py
class PostRepositoryPort(ABC):
    @abstractmethod
    def create(self, post: Post) -> Post: ...

    @abstractmethod
    def filter(self, post_id: UUID) -> Optional[Post]: ...
```

* `/domain/use_cases`: **Casos de uso** con un contrato común. Mantienen la lógica de aplicación y coordinan repos/servicios.

```python
# src/domain/use_cases/base_use_case.py
class BaseUseCase(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

# src/domain/use_cases/filter_posts_use_case.py
class FilterPostsUseCase(BaseUseCase):
    def __init__(self, repo: PostRepositoryPort):
        self.repo = repo

    def execute(self, expire: Optional[bool] = None, route:Optional[UUID] = None, owner:Optional[UUID] = None) -> dict:
        return self.repo.filter(expire,route,owner)
```

#### Adapters
Implementaciones concretas de los puertos definidos en `ports`.

```python
# src/adapters/database/post_repository_adapter.py
class PostgresUserRepositoryAdapter:
    """Postgres implementation of UserRepository using SQLAlchemy."""

    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def _get_session(self):
        """Create a new database session."""
        return self.SessionLocal()

    def create(self, post_dto: PostCreationRequest) -> Post:
        with self._get_session() as db:
            if not all([post_dto.routeId, post_dto.expireAt, post_dto.userId]):
                raise MissingPostInformationError("Route Id, Expiration date, and User id are all required.")
            
            if post_dto.expireAt <= datetime.now(timezone.utc):
                raise InvalidExpirationDate("Expiration date must be in the future.")
            
            new_id = self.sequence()
            time_now = datetime.now(timezone.utc)

            orm_post = PostDB(
                id = new_id,
                routeId = post_dto.routeId,
                userId = post_dto.userId,
                expireAt = post_dto.expireAt,
                createdAt = time_now
            )

            db.add(orm_post)
            db.commit()
            db.refresh(orm_post)
            return self._to_domain(orm_post)
```

> **Nota**: La app separa claramente **errores de entrada** vs **credenciales**. Evite usar `InvalidCredentialsError` para validaciones como UUID inválidos; use, por ejemplo, `InvalidInputError` (ver [Errores](#errores)).

#### Entrypoints

Routers FastAPI que exponen los casos de uso. Mantienen mínima lógica e inyectan dependencias vía **Depends**.

```python
# src/entrypoints/api/routers/post_router.py
router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("")
def filter_posts(
    expire: bool | None = Query(None, description="true=expired, false=not expired"),
    route: UUID | None = Query(None, description="route id"),
    owner: UUID | None = Query(None, description="owner/user id"),
    use_case: BaseUseCase = Depends(build_filter_post_use_case),
):
    return use_case.execute(expire=expire, route=route, owner=owner)
```

Agregue los routers en `main.py`:

```python
app = FastAPI(title=Settings.app_name)
app.include_router(post_router)
```

#### Configuración y ensamble

* `settings.py/config.py`: lectura de **variables de entorno** (ej.: `DATABASE_URL`, `LOG_LEVEL`, `APP_NAME`).
* `assembly.py`: **inyección de dependencias** (instanciación de repositorios y construcción de Casos de Uso).

```python
# src/assembly.py
_repo: PostRepositoryPort = PostgresUserRepositoryAdapter()

def build_filter_post_use_case() -> BaseUseCase:
    return FilterPostsUseCase(_repo)
```

#### Errores

Centralice excepciones personalizadas y mapee a HTTP con handlers.

```python
# src/errors.py
class InvalidInputError(Exception):
    pass

class PostNotFoundError(Exception):
    pass

class AuthError(Exception):
    pass
```

```python
# src/entrypoints/api/main.py
app = FastAPI()

@app.exception_handler(InvalidInputError)
async def invalid_input_handler(_: Request, exc: InvalidInputError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

---

### Configuración

Este proyecto usa **Poetry** para dependencias y configuración de herramientas en `pyproject.toml` (linters, pytest, etc.).

Recomendaciones:

* Dependencias de producción en `[tool.poetry.dependencies]`:

```bash
poetry add <libreria>
```

* Dependencias de desarrollo en el grupo `dev`:

```bash
poetry add <libreria> --group dev
```

* Configure linters y herramientas (ej.: `[tool.ruff]`, `[tool.isort]`, `[tool.pydoclint]`, `[tool.bandit]`).
* Configure pytest en `[tool.pytest.ini_options]` y variables de entorno de pruebas.
* Si modifica `pyproject.toml`, regenere el lock:

```bash
poetry lock
```

> **Variables de entorno sugeridas**: `DATABASE_URL`, `APP_NAME`, `APP_VERSION`, `LOG_LEVEL`.

---

## Ejecución de la aplicación

### 1. Instale las dependencias

```bash
poetry install
# Si no existe poetry.lock
# poetry lock
```

### 2. Ejecución

Ejecute con Poetry para usar el venv administrado:

```bash
PYTHONPATH=$(pwd)/src poetry run uvicorn entrypoints.api.main:app --host 0.0.0.0 --port 9000
```

El API quedará en `http://localhost:9000`.

Cargue `tests/api/posts.postman_collection.json` en Postman y configure la variable `baseUrl`.

---

## Ejecutar en Docker

> **Importante (desarrollo)**: el despliegue en K8s requiere la imagen llamada exactamente **`post-app:1.0.0`**.

```bash
# Opcional: exporte variables de proyecto
APP_NAME=post-app
APP_VERSION=1.0.0

# Build multi-stage (target runner)
docker build --rm --platform linux/amd64 -t ${APP_NAME}:${APP_VERSION} -f Dockerfile --target runner --label version=${APP_VERSION} .

# Run
docker run --platform linux/amd64 -p 9000:9000 ${APP_NAME}:${APP_VERSION}
```

---

## Ejecutar en Minikube/Kubernetes

```bash
minikube start --cpus=2 --memory=3g --cni calico

# Opción A (recomendada en minikube): construir dentro del daemon de minikube
eval $(minikube docker-env)
docker build -t post-app:1.0.0 -f Dockerfile --target runner .

# Opción B: construir local y cargar
# minikube image load post-app:1.0.0

# Desplegar manifests
yaml_dir=k8s
kubectl apply -f ${yaml_dir}

# Ver servicio
env SVC=$(kubectl get svc -o name | grep posts) && minikube service ${SVC#service/}
```

**Consejos de desarrollo con tag fijo (`post-app:1.0.0`)**

* Configure el Deployment con `imagePullPolicy: Always` o reinicie el rollout tras reconstruir:

```bash
kubectl rollout restart deployment/post-app
# Si su cluster no re‑pull por policy IfNotPresent, fuerce reinicio de pods:
kubectl delete pod -l app=post-app
```

---

## Uso de API.

La API tiene 7 endpoints:

* `POST /posts/` – Crea un Post 
* `GET /posts/{post_id}` – Obtiene un Post por id
* `GET /posts/` – Lista Posts con filtros

  * **Query params**:

    * `expire: bool | None` – `true`=expirados, `false`=vigentes
    * `route: UUID | None`
    * `owner: UUID | None`
* `PUT /posts/{post_id}` – Actualiza un Post (parcial o total, según implementación)
* `DELETE /posts/{post_id}` – Borra un Post
* `GET /posts/count` – Devuelve conteo para paginación
* `GET /posts/ping` – Checkeo de salud del servicio

**Documentación interactiva** (tras levantar la app):

* Swagger UI: `http://localhost:9000/docs`

---

## Post Model

Un **Post** expone, al menos, los siguientes campos:

* `id`: UUID (auto-generado)
* `title`: String (requerido)
* `content`: String (requerido)
* `owner`: UUID (opcional)
* `route`: UUID (opcional)
* `expireAt`: datetime (opcional)
* `createdAt`: datetime (servidor)

---

## Pruebas

El proyecto contempla **pruebas unitarias** y **pruebas de API (integración)**.

### Unitarias

Siga la misma estructura de `src`:

```
# Ejemplo
src/domain/models/post.py            -> tests/unit/domain/models/test_post.py
src/adapters/database/...            -> tests/unit/adapters/database/test_post_repo.py
```

Use **fixtures** de pytest en `conftest.py`:

```bash
poetry install
poetry run pytest --cov=src -v -s --cov-fail-under=70 --cov-report term-missing
```

### Integración

* Cargue la colección **`tests/api/posts.postman_collection.json`** en Postman.
* Ejecútela localmente o con **Newman**:

```bash
npx newman run tests/api/posts.postman_collection.json \
  --env-var baseUrl=http://localhost:9000
```

> Estas pruebas pueden ejecutarse automáticamente en CI.

---

## Cómo contribuir

* Siga un **flujo de ramas** (feature branches + PRs revisados).
* Mantenga los **routers delgados** y la lógica en **casos de uso**.
* Agregue/actualice **tests** por cada cambio funcional.
* Ejecute linters y pruebas localmente antes de abrir PR.

---

## Licencia

Este proyecto está licenciado bajo **MIT** – ver [LICENSE](LICENSE).

---

## Autor

* **Manuel E. Estevez-Bretón Ruiz** – [me.estevez-breton10@uniandes.edu.co](mailto:me.estevez-breton10@uniandes.edu.co)