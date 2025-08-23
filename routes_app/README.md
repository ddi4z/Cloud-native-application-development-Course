Servicio de Rutas (routes_app) 
Este microservicio es responsable de gestionar toda la lógica de negocio relacionada con los trayectos. Expone una API REST para crear, consultar, listar y eliminar trayectos.

Arquitectura
El servicio sigue los principios de Clean Architecture, separando las responsabilidades en las siguientes capas principales:
* domain: Contiene la lógica de negocio y las entidades (por ejemplo, el modelo Trayecto), sin dependencias externas.
* adapters: Implementaciones concretas de tecnologías externas, como la conexión a la base de datos (PostgreSQL o en memoria).
* entrypoints: El punto de entrada a la aplicación. En este caso, es la entrada a la API REST construida con FastAPI que expone los casos de uso al exterior.

Stack de Tecnologías
* Lenguaje: Python 3.11
* Framework API: FastAPI
* Dependencias: Poetry
* DB: PostgreSQL
* Testing: Pytest, Pytest-Cov, TestClient

Corrida en local
Pasos para configurar y ejecutar el sertvicio en local

Prerrequisitos
* Python 3.11 o superior
* Poetry instalado
* Docker

1. Instalación de Dependencias
Navegar a carpeta routes_app y ejecuta el siguiente comando para instalar las librerías necesarias:

poetry install

2. Configuración de Variables de Entorno
Este servicio requiere una conexión a una base de datos PostgreSQL. Se puede levantar una instancia localmente usando Docker:

docker run --name routes-db -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres

Luego, se crea un archivo .env en la raíz de la carpeta routes_app con el siguiente contenido:

# .env
DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/postgres"

3. Ejecución de la Aplicación
Para iniciar el servidor de FastAPI, activa el entorno virtual de Poetry y ejecuta uvicorn:

# Activa el entorno virtual
poetry shell

# Inicia el servidor con recarga automática
uvicorn routes_app.entrypoints.api.main:app --reload

La API estará disponible en http://127.0.0.1:8000.

Pruebas
El proyecto cuenta con un conjunto de pruebas unitarias y de integración para garantizar la calidad y el correcto funcionamiento del código.

Ejecución de Todas las Pruebas
Para correr todas las pruebas y ver un reporte de cobertura, ejecuta el siguiente comando desde la raíz de routes_app:

poetry run pytest --cov=routes_app

El objetivo es mantener una cobertura superior al 70%.

🗺️ Estructura del Proyecto
routes_app/
├── src/
│   └── routes_app/
│       ├── adapters/       # Conexión a BD (Postgres, Memoria)
│       ├── domain/         # Lógica de negocio y modelos
│       └── entrypoints/    # API REST con FastAPI
├── tests/
│   ├── integration/      # Pruebas de API (TestClient)
│   └── unit/             # Pruebas unitarias (modelos, casos de uso)
├── .env                  # Variables de entorno (no versionado)
├── Dockerfile            # Definición del contenedor
├── pyproject.toml        # Dependencias del proyecto (Poetry)
└── README.md             # Esta documentación

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/routes/ping` | Verifica el estado de salud del servicio. |
| `POST` | `/routes/reset` | **[Testing]** Elimina todos los datos de la BD. |
| `POST` | `/routes/` | Crea un nuevo trayecto. |
| `GET` | `/routes/` | Lista todos los trayectos. |
| `GET` | `/routes/count` | Cuenta el número total de trayectos. |
| `GET` | `/routes/{trayecto_id}` | Obtiene un trayecto específico por su ID. |
| `DELETE` | `/routes/{trayecto_id}` | Elimina un trayecto por su ID. |