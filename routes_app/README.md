# routes_app – Servicio de Trayectos

Este proyecto es una **aplicación FastAPI** que implementa arquitectura hexagonal (puertos y adaptadores) para gestionar la entidad **Trayecto**. La app está diseñada para ser agnóstica a la capa de persistencia, con implementaciones para **PostgreSQL** y una base de datos en **memoria**. Puede ejecutarse localmente, en **Docker** y en **Kubernetes/Minikube**.

## Índice

1.  [Estructura del Proyecto](#estructura-del-proyecto)
2.  [Ejecución de la Aplicación](#ejecución-de-la-aplicación)
3.  [Ejecutar en Docker](#ejecutar-en-docker)
4.  [Ejecutar en Minikube/Kubernetes](#ejecutar-en-minikubekubernetes)
5.  [Endpoints de la API](#endpoints-de-la-api)
6.  [Pruebas](#pruebas)
7.  [Autor](#autor)

## Estructura del Proyecto

La aplicación sigue los principios de la arquitectura hexagonal para separar el dominio de la infraestructura.
```
routes_app/
├── src/
│   └── routes_app/
│       ├── adapters/               # Implementaciones de los puertos
│       │   ├── memory/             # Adaptador de repositorio en memoria
│       │   └── postgres/           # Adaptador de repositorio para PostgreSQL
│       ├── domain/                 # Lógica de negocio y modelos de dominio
│       │   ├── models/             # Modelos de Pydantic para la entidad Trayecto
│       │   ├── ports/              # Interfaces (contratos) para repositorios
│       │   └── use_cases/          # Lógica de aplicación que orquesta el dominio
│       ├── entrypoints/            # Puntos de entrada de la aplicación
│       │   └── api/                # API REST con FastAPI (routers y main)
│       ├── assembly.py             # Inyección de dependencias y ensamblaje de casos de uso
│       └── errors.py               # Excepciones personalizadas
├── tests/
│   ├── api/                        # Pruebas de integración y colección de Postman
│   └── unit/                       # Pruebas unitarias por capa
│       ├── adapters/
│       └── domain/
│           ├── models/
│           └── use_cases/
├── Dockerfile                      # Definición de la imagen Docker multi-etapa
├── pyproject.toml                  # Dependencias del proyecto y configuración (Poetry)
└── README.md                       # Esta documentación
```

### Dominio

Contiene el núcleo de la lógica de negocio.

* **/domain/models**: Define la entidad `Trayecto` usando Pydantic, incluyendo validaciones de negocio.
    ```python
    # src/routes_app/domain/models/models.py
    class Trayecto(BaseModel):
        """Modelo de dominio para la entidad Trayecto."""
        id: UUID = Field(default_factory=uuid4)
        flightId: str
        sourceAirportCode: str
        destinyAirportCode: str
        bagCost: int
        plannedStartDate: datetime
        plannedEndDate: datetime

        @field_validator('sourceAirportCode', 'destinyAirportCode')
        @classmethod
        def validate_airport_code(cls, v: str) -> str:
            """Valida que el código de aeropuerto sea un string de 3 letras..."""
            if not v.isalpha() or len(v) != 3:
                raise ValueError(f"'{v}' Código de aeropuerto inválido...")
            return v.upper() ...
    ```
* **/domain/ports**: Define las interfaces que la lógica de negocio utiliza para interactuar con sistemas externos, como la base de datos.
    ```python
    # src/routes_app/domain/ports/routes_repository_port.py
    class RoutesRepositoryPort(ABC):
        @abstractmethod
        def create(self, trayecto: Trayecto) -> Trayecto:
            """Crea una instancia de Trayecto y lo retorna"""
            raise NotImplementedError
    ```
* **/domain/use_cases**: Contiene la lógica de aplicación que orquesta los modelos y repositorios para cumplir con los requisitos funcionales.
    ```python
    # src/routes_app/domain/use_cases/create_trayecto_use_case.py
    class CreateTrayectoUseCase(BaseUseCase):
        """Caso de uso para crear un trayecto."""
        def __init__(self, repository: RoutesRepositoryPort):
            self.repository = repository

        def execute(self, trayecto: Trayecto) -> Trayecto:
            return self.repository.create(trayecto)
    ```

### Adaptadores

Contiene implementaciones concretas de los puertos. Este proyecto incluye dos:
* **InMemoryRoutesRepositoryAdapter**: Una implementación en memoria, útil para pruebas y desarrollo rápido. 
* **PostgresRoutesRepositoryAdapter**: Una implementación con PostgreSQL y SQLAlchemy para persistencia real.

### Entrypoints

Define cómo el mundo exterior interactúa con la aplicación. En este caso, es una API REST construida con FastAPI.

```python
# src/routes_app/entrypoints/api/routers/routes.py
router = APIRouter(tags=["Trayectos"])

@router.post("/", response_model=TrayectoOut, status_code=201)
def create_trayecto(
    payload: TrayectoIn,
    use_case: BaseUseCase = Depends(build_create_trayecto_use_case),
    # ...
):
    """Crea un nuevo trayecto."""
    # ...
    trayecto_a_crear = Trayecto(**payload.model_dump())
    nuevo_trayecto = use_case.execute(trayecto_a_crear)
    return TrayectoOut.model_validate(nuevo_trayecto.model_dump())
```


### Ensamblaje (Assembly)
El archivo `src/routes_app/assembly.py` se encarga de la inyección de dependencias. Aquí se decide qué implementación del repositorio (InMemory o Postgres) se usará en los casos de uso. 

```python
# src/routes_app/assembly.py

# repository: RoutesRepositoryPort = InMemoryRoutesRepositoryAdapter()
repository: RoutesRepositoryPort = PostgresRoutesRepositoryAdapter()

def build_create_trayecto_use_case() -> BaseUseCase:
    """Construye el caso de uso para crear un trayecto."""
    return CreateTrayectoUseCase(repository)
```

## Ejecución de la Aplicación
Siga estos pasos para instalar y ejecutar la aplicación:

**1. Prerrequisitos**
* Python 3.11+
* Poetry
* Docker
* Minikube / Kubernetes (opcional, para despliegue)

**2. Instalar Dependencias**
Navega a la carpeta `routes_app` y ejecuta:
```bash
   poetry lock
   poetry install
```

**3. Seleccionar Adaptador de Base de Datos**
Edita el archivo `src/routes_app/assembly.py` para elegir la implementación del repositorio:
* Adaptador en Memoria: Descomenta la línea de InMemoryRoutesRepositoryAdapter.
* Adaptador PostgreSQL: Descomenta la línea de PostgresRoutesRepositoryAdapter. Si eliges esta opción, asegúrate de tener una instancia de PostgreSQL en ejecución y configurar la variable de entorno **DATABASE_URL**.

**4. Ejecutar la Aplicación Localmente**
Para iniciar el servidor de FastAPI, ejecuta el siguiente comando desde la raíz del proyecto:
```
poetry run uvicorn routes_app.entrypoints.api.main:app --host 0.0.0.0 --port 8000
```
La API estará disponible en http://127.0.0.1:8000.

## Ejecutar en Docker
El `Dockerfile` utiliza una construcción multi-etapa para crear una imagen ligera y segura.

**1. Construir la imagen Docker:**
```bash
docker build -t routes-app:1.0.0 .
```
**2. Ejecutar el contendor**
```bash
docker run --rm -p 8000:8000 -e DATABASE_URL="<tu_cadena_de_conexion>" routes-app:1.0.0
```

## Ejecutar en Minikube/Kubernetes
**1. Iniciar Minikube:**

```bash
minikube start --cpus=2 --memory=3g --cni calico
```
**2. Construir la imagen dentro del entorno de Minikube:**
```bash
eval $(minikube docker-env)
docker build -t routes-app:1.0.0 .
```
**3. Desplegar los manifiestos de Kubernetes:** Asegúrate de tener un archivo `routes_app.yaml` en una carpeta k8s/ con la definición del Deployment y el Service.
```bash
kubectl apply -f k8s/routes_app.yaml
```
**4. Exponer y acceder al servicio:**
```bash
minikube service routes-app-service
```

## Endpoints de la API
| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/routes/ping` | Verifica el estado de salud del servicio. |
| `POST` | `/routes/reset` | **[Testing]** Elimina todos los datos de la BD. |
| `POST` | `/routes/` | Crea un nuevo trayecto. |
| `GET` | `/routes/` | Lista todos los trayectos. |
| `GET` | `/routes/count` | Cuenta el número total de trayectos. |
| `GET` | `/routes/{trayecto_id}` | Obtiene un trayecto específico por su ID. |
| `DELETE` | `/routes/{trayecto_id}` | Elimina un trayecto por su ID. |

## Pruebas
El proyecto incluye pruebas unitarias y de integración para garantizar la calidad del código. La estructura de pruebas refleja la del código fuente.

### Ejecutar Pruebas
Para ejecutar todas las pruebas unitarias y obtener un informe de cobertura (se requiere un 70% como mínimo), utiliza el siguiente comando:
```bash
poetry run pytest --cov=src/routes_app --cov-report=term-missing --cov-fail-under=70
```
### Pruebas de API
En la carpeta tests/api/ se encuentra una colección de Postman (`routes.postman_collection.json`) que puede ser importada para realizar pruebas de integración contra la API desplegada.

## Autor
Jorge Paternina – j.paterninam@uniandes.edu.co