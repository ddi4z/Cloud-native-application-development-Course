# `offers_app` -

Este proyecto es el desarrollo de una aplicación con FastAPI que implementa una arquitectura hexagonal (también conocida como puertos y adaptadores) para gestionar la entidad `Offer`. La aplicación se ejecuta haciendo uso de docker y puede ser ejecutada directamente en su ambiente o haciendo uso de k8s.

## Tabla de contenido

- [`offers_app`](#offers-app---proyecto-ejemplo)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Requisitos](#requisitos)
  - [Estructura del Proyecto](#estructura-del-proyecto)
    - [Carpeta src](#carpeta-src)
      - [Domain](#domain)
      - [Adapters](#adapters)
      - [Entrypoints](#entrypoints)
      - [Configuración y ensamble](#configuración-y-ensamble)
      - [Errores](#errores)
    - [Configuración](#configuración)
  - [Ejecución de la aplicación](#ejecución-de-la-aplicación)
    - [1. Instale las dependencias:](#1-instale-las-dependencias)
    - [2. Ejecución](#2-ejecución)
  - [Ejecutar en Docker](#ejecutar-en-docker)
  - [Ejecutar en minikube](#ejecutar-en-minikube)
  - [API Endpoints](#api-endpoints)
  - [Pruebas](#pruebas)
    - [Unitarias](#unitarias)
    - [Integración](#integración)
  - [Cómo contribuir](#cómo-contribuir)
  - [Licencia](#licencia)
  - [Autor](#autor)


## Requisitos

- Python 3.11
- Poetry version 2.1.1
- Docker
- Postman

## Estructura del Proyecto

```
.
├── src/
│   ├── domain/             # Capa de dominio
│   │   ├── models/         # Modelos de dominio
│   │   ├── ports/          # Puertos (interfaces)
│   │   └── use_cases/      # Casos de uso
│   ├── adapters/           # Capa de adaptadores
│   │   └── database/       # Adaptador de base de datos
│   └── entrypoints/        # Puntos de entrada
│       └── api/            # API REST
├── tests/                  # Pruebas
│   ├── domain/             # Pruebas de la capa de dominio
│   │   ├── models/         # Pruebas de los modelos
│   │   ├── ports/          # Pruebas de los puertos
│   │   └── use_cases/      # Pruebas de los casos de uso
│   ├── adapters/           # Prueba de los adaptadores
│   └── entrypoints/        # Prueba de la API y puntos de entrada
├── Dockerfile              # Configuración de Docker
├── pyproject.toml          # Configuración de Poetry
└── README.md               # Este archivo
```

### Carpeta src

Esta carpeta contiene el código y la lógica de la aplicación que permite exponer el API y puede integrar otras aplicaciones o componentes si lo requiere.

#### Domain

Carpeta con la lógica de la aplicación.

- `/domain/models`: Contiene las clases que representan las entidades necesarias para los casos de uso de la aplicación. Comúnmente estos modelos son usados para el almacenamiento en la base de datos, pero no deben confundirse, estas clases no deben estar acopladas a una base de datos en específico y solo representan las entidades que se van a manipular en los casos de uso. Será responsabilidad de los adaptadores transformarlas y almacenarlas en una determinada base de datos. En este ejemplo los modelos estarán soportados haciendo uso de pydantic por facilidad de validación e integración con FastAPI.

- `/domain/ports`: Contiene las interfaces que habilitan la interacción con componentes o lógica externa. Estas clases no son implementaciones sino únicamente el "template" que deben seguir nuestras integraciones. Esto permite desacoplar la implementación, habilitando que se pueda reemplazar fácilmente los componentes con los que se integra la aplicación, siempre y cuando se respecte la definición de las interfaces. En este proyecto encontrará que se hace uso de una clase llamada [Repository](https://martinfowler.com/eaaCatalog/repository.html) la cual sigue un patrón que es comúnmente usado cuando el puerto es usado para almacenamiento de una entidad. Sin embargo, los puertos pueden seguir otros patrones para interactuar con otros componentes, por ejemplo notificaciones.

- `/domain/use_cases`: Contiene los casos de uso de la aplicación, almacenar, consultar, modificar, borrar o cualquier otra funcionalidad (obtener el número de registros o limpiar la base de datos). Todos los casos de usos deben compartir el mismo contrato. Para ello deben extender de una interfaz que define como es el comportamiento de los casos de uso, esta interfaz resulta ser clave para permitir que los entrypoints de la aplicación puedan interactuar con los casos de uso sin generar acoplamiento.

#### Adapters

En la carpeta adapters se encuentra la implementación de los puertos definidos en la carpeta de ports. En este proyecto de ejemplo se encuentra una implementación de un almacenamiento en memoria, pero usted puede seguir el mismo schema si quiere realizar una implementación para almacenar en una base de datos. **En particular, en el proyecto se realizaron dos implementaciones una en memoria y otra con PostgreSQL. La que corresponde al adaptador de "en memoria" facilito las pruebas sobre los casos de uso.**

#### Entrypoints

Contiene los archivos que servirán como punto de acceso a la aplicación; también podrían considerarse como puertos de ingreso. En esta carpeta se encuentran las funciones o clases que permiten interactuar con los casos de uso.

En este proyecto se hace uso de routers donde se definen las rutas y los métodos HTTP que se soportan. Si usted quiere agregar nuevas rutas, debe agregar otro archivo router o modificar el actual siguiendo el mismo patrón.

Posteriormente debe agregar el router a la aplicación en el archivo `main.py`. Todo esto ya se encuentra hecho. 

#### Configuración y ensamble

- `config.py`: En este archivo se encuentran las funciones que permiten leer las variables de ambiente o constantes que se usan en todo el proyecto. Es una buena práctica consolidar el manejo de las variables de ambiente y constantes a un solo archivo, facilita las pruebas y la mantenibilidad.
- `assembly.py`: Este archivo contiene las funciones que realizan la inyección de dependencias. Como ha podido ver en todos los ejemplos previos, las asociaciones entre las clases y funciones se realizan por medio de interfaces, ninguna clase conoce o usa una implementación en particular. Es en este paquete donde se instancian las implementaciones que se van a usar y las cuales son usadas por cada router:

#### Errores

En el proyecto se encuentra el archivo `errors.py` el cual está diseñado para albergar todas las clases de excepciones personalizadas que se creen en el proyecto. Recomendamos crear sus propias clases de excepción para tener mayor control del flujo del programa.

```python
class OfferNotFoundError(Exception):
    """Exception raised when a offer is not found."""
    pass
```

Las excepciones se manejan en los puntos de entrada de la app como por ejemplo:

```python
try:
  ...
except OfferNotFoundError as e:
  raise HTTPException(status_code=404, msg=str(e))
```

### Configuración

Este proyecto hace uso de [poetry](https://python-poetry.org/) para la gestión de dependencias y configuración de algunas librerías usadas en el proyecto. Encontrará la configuración en el archivo `pyproject.toml` el cuál ya es un estandar para la configuración de proyectos en Python. [Documentación](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

> Recomendación: procure evitar otros archivos de configuración como el `setup.cfg`, `setup.py`, `<archivo>.ini` u otros, con el fin de mejorar la mantenibilidad de nuestro código y evitar errores por conflictos de configuración.

Algunos puntos que tener en cuenta en la configuración:

- Agregue todas las dependencias que se usarán en producción en el group por defecto `[tool.poetry.dependencies]`. Esto sucederá por defecto al usar el comando add de poetry: 
```bash
poetry add <libreria>
```
- Agregue las dependencias de desarrollo en el grupo `dev`. Para esto defina el grupo cuando agregue la librería:
```bash
poetry add <librería> --group dev
```
- El archivo contiene las reglas de configuración de linters y herramientas de análisis habilitadas en el proyecto. `[tool.isort]`, `[tool.bandit]`, `[tool.pydoclint]`, `[tool.ruff]`. Si desea modificar las reglas o conocer más de ellas puede revisar los links en cada sección.
- El archivo contiene las reglas de configuración para la ejecución de pruebas con pytest. En la sección `[tool.pytest.ini_options]` puede modificar o agregar nuevas reglas de pruebas. Así como las variables de ambiente que se usarán en las pruebas.

Siempre que modifique el archivo, recomendamos regenerar el archivo de poetry.lock usando:
```bash
poetry lock
```

## Ejecución de la aplicación

### 1. Instale las dependencias:
```bash
poetry install

# Si no existe el archivo poetry.lock ejecute primero
# poetry lock
```
Poetry instalará todas las dependencias en un ambiente virtual gestionado por Poetry.

### 2. Ejecución

dado que todas las dependencias están instaladas en una ambiente virtualizado y gestionado por Poetry es necesario correr el servidor haciendo uso de Poetry:
```bash
PYTHONPATH=$(pwd)/src poetry run uvicorn entrypoints.api.main:app --host 0.0.0.0 --port 9000
```

Lo anterior si utiliza un sistema operativo basado en UNIX, de lo contrario haga esto si esta utilizando Windows:

```powershell
$env:PYTHONPATH = $pwd\src
poetry run uvicorn src.entrypoints.api.main:app --host 0.0.0.0 --port 9000 --reload
```

El API estará disponible en `http://localhost:9000`

Cargue el archivo `offers_app/tests/api/offers.postman_collection.json` en su postman y reemplace la variable `baseUrl` por la url.

Ejecute las pruebas y verifique que se completa correctamente.

## Ejecutar en Docker

```bash
APP_VERSION = ... # use la misma versión del documento pyproject.toml
APP_NAME = ... # use el mismo definido en el documento pyproject.toml
docker build --rm --platform linux/amd64 -t ${APP_NAME}:${APP_VERSION} -f Dockerfile --target runner --label version=${APP_VERSION} .

docker run --platform linux/amd64 -p 9000:9000 ${APP_NAME}:${APP_VERSION}
```

## Ejecutar en minikube

Después de haber creado la imagen haciendo uso de docker, ejecute:

```bash
minikube start --cpus=2 --memory=3g --cni calico

#make mkbuild
minikube image load ${APP_NAME}:${APP_VERSION}

kubectl apply -f k8s
minikube service offers-service
```

Minikube asignará un puerto para que pueda acceder a su servicio. Puede usarlo en su browser o en postman.

## API Endpoints

- `GET /offers/ping/` - Endpoint para saber la salud del servicio
- `GET /offers/count/` - Cuenta los registros en base de datos
- `GET /offers/reset/` - Limpia la base de datos
- `POST /offers/` - Crea una ofera
- `GET /offers/{offer_id}` - Trae una oferta en específico
- `GET /offers/` - Trae todas las ofertas 
- `DELETE /offers/{offer_id}` - Borra una oferta
  
Accede a la documentación después de ejecutar la aplicación:
- Swagger UI: `http://localhost:9000/docs`

---

El proyecto contempla dos paquetes de pruebas: pruebas unitarias y pruebas de API (Integración).

### Unitarias

Si está usando pytest para sus pruebas, utilice [fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html) para crear recursos reutilizables en las pruebas. Esto mejorará su código y permitirá que las pruebas sean consistentes. Estos fixtures deben estar ubicados en un archivo `conftest.py` y no en los archivos de pruebas.

Para ejecutar las pruebas unitarias y establecer el porcentaje mínimo de cobertura del conjunto de pruebas en 70%, ejecuta el siguiente comando:

```bash
poetry install
poetry run pytest --cov=src -v -s --cov-fail-under=70 --cov-report term-missing
```

Por último, recuerde que la configuración de pytest está en el archivo `pyproject.toml`, ajuste la sección dependiendo de las necesidades que tenga. Acuda a la [documentación](https://docs.pytest.org/en/stable/reference/customize.html) si lo requiere.

### Integración

Las pruebas de integración se realizan por medio de postman y newman. Encontrará un archivo de colección de postman en la carpeta `tests/api/` el cuál puede cargar en su aplicación de postman de manera local. Posteriormente puede ejecutar `Run collection` para verificar que la aplicación está funcionando correctamente.

Estas pruebas son ejecutadas de manera automática en los pipelines de pruebas.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

- César Forero - [ca.forero10@uniandes.edu.co](mailto:ca.forero10@uniandes.edu.co)
- Javier Barrera (adaptación de la documentación acorde a la API desarrollada)  - [js.barrerat1@uniandes.edu.co](mailto:js.barrerat1@uniandes.edu.co)
