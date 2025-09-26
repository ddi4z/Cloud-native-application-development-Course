# Users app

Este proyecto es una **aplicación FastAPI** que implementa arquitectura hexagonal (puertos y adaptadores) para gestionar la entidad **User**. La app puede ejecutarse localmente, en **Docker** y en **Kubernetes/Minikube**.

## Índice

1. [Estructura](#estructura)  
2. [Ejecución](#ejecución)  
3. [Uso](#uso)  
4. [Pruebas](#pruebas)  
6. [Autor](#autor)  

## Estructura

La aplicación se organiza de la siguiente manera:

```
.
├── src/
│   ├── domain/             # Capa de dominio
│   │   ├── models/         # Entidades y modelos de negocio
│   │   ├── ports/          # Interfaces (puertos)
│   │   └── use_cases/      # Lógica de negocio (casos de uso)
│   ├── adapters/           # Adaptadores de infraestructura
│   │   └── postgres/       # Implementación con base de datos PostgreSQL
│   │   └── memory/         # Implementación en memoria (para pruebas locales)
│   ├── entrypoints/        # Puntos de entrada a la aplicación
│   │   └── api/            # API REST (FastAPI)
│   └── assembly.py         # Ensamblaje de casos de uso con repositorios
├── tests/                  # Pruebas unitarias e integración
├── Dockerfile              # Configuración de la imagen Docker
├── pyproject.toml          # Dependencias y configuración de Poetry
└── README.md               # Documentación del proyecto
```

## Ejecución

Siga estos pasos para instalar y ejecutar la aplicación:

1. Instalar dependencias:
   ```bash
   poetry lock
   poetry install
   ```

2. Seleccionar el adaptador en `src/assembly.py`:
   - **Adaptador en memoria**: descomente el adaptador en memoria y comente el de PostgreSQL.  
   - **Adaptador PostgreSQL** (por defecto): descomente PostgreSQL y comente el de memoria.  
     > Debe tener una base de datos PostgreSQL provisionada y definir la variable de entorno `DATABASE_URL`, por ejemplo:
     ```bash
         DATABASE_URL=postgresql://user:password@localhost:5432/dbname
     ```

3. Ejecutar la aplicación (para Docker):
   ```bash
   poetry run uvicorn src.entrypoints.api.main:app --host 0.0.0.0 --port 9000
   ```

4. Construir la imagen para Minikube (para Minikube):
   ```bash
   minikube docker-env | Invoke-Expression
   docker build -t users-app:v1.0.0 .
   ```

## Uso

Una vez levantado el contenedor:

- Si corre con **Docker**:
  ```
  http://localhost:9000/users
  ```
- Si corre en **Minikube**, use la URL generada al exponer el servicio.  

La API REST expone los endpoints documentados en el curso y puede ser consumida desde cualquier cliente HTTP (ej. Postman, navegador).

## Pruebas

Las pruebas cubren principalmente adaptadores, casos de uso y modelos.  

Para ejecutarlas:

```bash
poetry run pytest --cov=src -v -s --cov-fail-under=70 --cov-report term-missing
```

## Autor

**Daniel Felipe Diaz Moreno** 
