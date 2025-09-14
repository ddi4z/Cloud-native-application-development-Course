## Vista de desarollo 

Se opta por utilizar una estructura similar a las 4 aplicaciones, así como para los nuevos requerimientos (RF003 - RF005). Tomando como base la arquitectura hexagonal (puertos y adaptadores) se definen las carpetas `domain`, `adapters` y `entrypoints`. En la primera carpera se almacenaran las clases del dominio, los puertos y los casos de uso, mientras que en la segunda y tercera carpeta irán respectivamente los adaptadores (implementaciones de los puertos) y los puntos de entrada a la aplicación, la API REST. 

Cabe mencionar que para los nuevos requerimientos no se desarrollaron pruebas unitarias, con lo cual el directorio `rf_00X_app/tests`, en el gráfico abajo no existe.

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


### Tabla de tecnologias

| Tecnología                                           | Descripción                                                                                                               | Desarrollo, ejecución, pruebas o despliegue |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Poetry                                               | Manejador de dependencias y empaquetado para proyectos en Python. Cada aplicación lo usa para gestionar sus dependencias. | Desarrollo                                  |
| FastAPI                                              | Framework moderno y rápido para construir APIs en Python. Todas las aplicaciones están desarrolladas con FastAPI.         | Desarrollo                                  |
| pytest                                               | Framework de pruebas para Python. Se usa para pruebas unitarias y de integración.                                         | Pruebas                                     |
| Postman                                              | Cliente para diseñar y probar APIs; se usó para pruebas manuales con colecciones.                                         | Pruebas                                     |
| Newman                                               | CLI para ejecutar colecciones de Postman en pipelines (automatiza pruebas de API).                                        | Pruebas, Despliegue                         |
| PlantUML                                             | Generación de diagramas (componentes y despliegue) a partir de texto.                                                     | Desarrollo                                  |
| Docker                                               | Plataforma de contenedores para empaquetar y ejecutar las apps (`*_app`). Imágenes publicadas en ECR.                     | Ejecución, Despliegue                       |
| Kubernetes                                           | Orquestación de contenedores (Pods, Services, Ingress, HPA) para cada servicio.                                           | Ejecución, Despliegue                       |
| Amazon EKS                                           | Servicio administrado de Kubernetes en AWS donde corre el clúster.                                                        | Despliegue, Ejecución                       |
| Ingress Controller (Nginx / AWS LB Controller + ALB) | Punto único de entrada HTTP(S) que enruta por host/path a `rf003`, `rf004`, `rf005`.                                      | Despliegue, Ejecución                       |
| Amazon ECR                                           | Registro de imágenes de contenedor desde donde los Pods hacen *pull*.                                                     | Despliegue                                  |
| Amazon RDS for PostgreSQL                            | Base de datos única en la nube (`platform_db`) con tablas por dominio.                                                    | Ejecución, Despliegue                       |
| AWS Secrets Manager / Kubernetes Secrets             | Gestión de credenciales (DB, tokens) usadas por los Pods/Services.                                                        | Despliegue, Ejecución                       |
| AWS IAM / IRSA                                       | Permisos mínimos para Pods hacia servicios AWS (ECR/RDS/Secrets).                                                         | Despliegue                                  |
| Amazon CloudWatch / Prometheus + Grafana             | Observabilidad: logs, métricas y trazas distribuidas.                                                                     | Ejecución, Despliegue                       |
| Minikube (opcional local)                            | Kubernetes local para desarrollo/pruebas rápidas antes de EKS.                                                            | Despliegue                                  |
| GitHub Actions                                       | CI/CD en GitHub: linting, pruebas (pytest/Newman) y *workflows* de integración.                                           | Desarrollo, Pruebas, Despliegue             |


