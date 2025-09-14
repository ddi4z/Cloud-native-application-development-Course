# Vistas de arquitectura

## Vista de componentes
  
![Vista de componentes](./diagrams/components.png "Vista de componentes")

Arquitectura por servicios con propiedad de datos por dominio y acoplamiento bajo, enfocada en cubrir funcionalidades esenciales de la segunda entrega.
## Descripción del sistema actualizado

### Actor (líneas punteadas)
El **User** interactúa vía **API REST** exclusivamente con los **nuevos servicios**:
- **RF-003 Crear publicación** → `POST /posts`
- **RF-004 Consultar publicación y ofertas** → `GET /posts/{postId}`
- **RF-005 Crear oferta** → `POST /offers`  

Autenticación por **Bearer JWT**.  
Los servicios de dominio se consumen de forma interna por los RF-003..005.

### Servicios (cajas rosadas)
- **Orquestadores/fachada:** `rf003_app`, `rf004_app`, `rf005_app` (exponen las APIs al usuario).  
- **Servicios de dominio:** `users_app`, `routes_app`, `posts_app`, `offers_app` (APIs internas).  

Todos son **desplegables de forma independiente** y se comunican entre sí vía **HTTP/JSON**  
(sin acceso directo a datos ajenos).

### Persistencia (cilindro azul)
- **Una sola base de datos** **PostgreSQL en la nube** (ej: Cloud SQL, RDS, Neon).  
- Cada servicio **posee sus propias tablas** (y/o *schema* lógico) dentro de esa BD única:  
  - `users.*`  
  - `routes.*`  
  - `posts.*`  
  - `offers.*`  
- **Sin llaves foráneas cruzadas** entre dominios; **no** se realizan *joins* entre tablas de servicios distintos.  
- La **propiedad y acceso** a cada tabla es exclusivo del servicio correspondiente;  
  el **intercambio entre dominios es vía APIs**.  
- Consistencia garantizada por **transacciones** y reglas de negocio en cada servicio.

### Entorno (env)
Un mismo **stack/cluster** (ej: Kubernetes + Ingress) encapsula los procesos y habilita  
**escalado y despliegue independientes** por servicio.  

Las conexiones a la BD en la nube se manejan mediante **secrets** y políticas de red/VPC.  
Se propaga `X-Request-Id` para trazabilidad.


### Componente RF-003
| Componente                  | RF-003                                                                 |
|----------------------------|----------------------------------------------------------------------------------------|
| Código/Id del componente   | RF-003                                                                                 |
| Tipo                       | Servicio orquestador expuesto por API HTTP/REST                                        |
| Responsabilidad            | 1) Recibir datos de la publicación y del trayecto.<br>2) Autenticar al usuario (solo usuarios con sesión).<br>3) Validar fechas: inicio de viaje **> ahora**; expiración **> ahora** y **≤** inicio de viaje.<br>4) Consultar si el trayecto existe; si no existe **crearlo** y usarlo; si existe **descartar** los datos recibidos y usar el almacenado.<br>5) Verificar que el usuario **no tenga** otra publicación para **el mismo trayecto**; si la tiene, **rechazar** la creación.<br>6) Crear la publicación asociándola al usuario autenticado y al trayecto decidido.<br>7) Asegurar **consistencia** al finalizar (éxito o error).   |
| Consideraciones de diseño  | **Idempotencia:** usar `Idempotency-Key` y/o restricción única `(user_id, route_id)` para evitar duplicados en reintentos.<br>**Concurrencia:** manejar carreras entre dos creaciones simultáneas (bloqueo optimista/únicos a nivel de posts).<br>**Transacciones/Consistencia:** transacción distribuida tipo *orchestrated saga* (crear trayecto → crear publicación; si falla publicación, **compensar** trayecto si se creó solo para esta operación).<br>**Fechas y zonas horarias:** comparar en **UTC**, definir claramente inclusiones (`expiración ≤ inicio`).<br>**Errores y contratos:** 400 validación, 401/403 autenticación, 409 conflicto (publicación duplicada para el mismo trayecto).<br>**Observabilidad:** trazas con `X-Request-Id`, logs estructurados y métricas de intentos/éxitos/fallos. ||
| Integraciones              | **Auth/Usuarios** (`users_app` o gateway): HTTP Bearer JWT; validar identidad y obtener `user_id` (sincronía).<br>**Rutas** (`routes_app`): `GET /routes?…` para buscar; `POST /routes` para crear cuando no exista (JSON/HTTP).<br>**Publicaciones** (`posts_app`): `GET /posts?owner={userId}&route={routeId}` para verificar duplicados; `POST /posts` para crear (JSON/HTTP).<br>**Comunicación:** síncrona REST, *timeouts* y reintentos con *backoff*; propagar `X-Request-Id`/`Idempotency-Key`. |           |

### Componente RF-004
| Componente                 | RF-004                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Código/Id del componente | `rf005.create_offer` (Use case `CreateOfferUseCase` expuesto vía `POST /offers`)                                                            |
| Tipo                  | Servicio orquestador (use case de dominio) expuesto por API HTTP/REST                                                                       |
| Responsabilidad       | 1) Recibir datos de la oferta y el **id de la publicación**.<br>2) Autenticar al usuario (solo sesión válida).<br>3) Validar que la publicación **existe**.<br>4) Verificar que la publicación **no haya expirado**.<br>5) Impedir que el usuario **oferte sobre su propia publicación**.<br>6) **Calcular el score** (utilidad) de la oferta.<br>7) Crear la oferta **asociándola** al usuario autenticado y a la publicación indicada, persistiendo el score.<br>8) Asegurar **consistencia** al finalizar (éxito o error). |
| Consideraciones de diseño | **Idempotencia:** aceptar `Idempotency-Key` para reintentos seguros; evitar duplicados de creación.<br>**Concurrencia:** varias ofertas pueden llegar simultáneamente; usar transacciones y niveles de aislamiento adecuados.<br>**Transacciones/Consistencia:** operaciones atómicas (leer publicación → calcular score → crear oferta). Si falla el cálculo del score o la persistencia, **rollback** completo.<br>**Fechas y zonas horarias:** validar expiración en **UTC** contra la hora del servidor.<br>**Seguridad:** 401/403 si no hay autenticación; 404 si la publicación no existe; 409/422 si la publicación está expirada o es del mismo usuario.<br>**Observabilidad:** `X-Request-Id`, métricas de intentos/éxitos/fallos, trazas distribuidas. |
| Integraciones         | **Auth/Usuarios** (gateway o `users_app`): JWT Bearer para identidad y `user_id` (síncrono).<br>**Publicaciones** (`posts_app`): `GET /posts/{postId}` para verificar existencia/expiración y dueño (JSON/HTTP).<br>**Ofertas** (`offers_app`): `POST /offers` para persistir la oferta (JSON/HTTP).<br>**Scores** (`scores_app`): `POST /scores/offers` (o equivalente) para calcular la utilidad antes de persistir; *timeouts* y reintentos con backoff; propagar `X-Request-Id`/`Idempotency-Key`. |

### RF-005
| Componente                 | Servicio **Consultar publicación y ofertas** (RF004)                                                                                         |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Código/Id del componente** | `rf004.get_post_details` (Use case `GetPostWithOffersUseCase` expuesto vía `GET /posts/{postId}/details`)                                      |
| **Tipo**                  | Servicio orquestador de lectura (consulta compuesta) expuesto por API HTTP/REST                                                               |
| **Responsabilidad**       | 1) Recibir el **id de la publicación**.<br>2) Autenticar y **autorizar**: solo el **propietario** puede consultar.<br>3) Obtener la publicación y su **trayecto** asociado.<br>4) Listar **ofertas** de la publicación.<br>5) Obtener/adjuntar la **utilidad (score)** de cada oferta y **ordenar** de forma **descendente** por score (los `null` al final).<br>6) Si la utilidad no se puede calcular/recuperar temporalmente, devolver `score: null` para esa oferta.<br>7) Responder con un objeto unificado: publicación + trayecto + ofertas (cada una con su score). |
| **Consideraciones de diseño** | **Autorización estricta:** 403 si el solicitante no es el dueño; 404 si la publicación no existe.<br>**Resiliencia:** *timeouts*, reintentos con backoff y *circuit breaker* hacia `scores_app`; degradar con `score: null` sin fallar toda la consulta; incluir `warnings` opcionales en la respuesta.<br>**Ordenamiento:** score descendente; tratar `null` como valor mínimo (queda al fina_


## Vista de despliegue

![Vista de despliegue](./diagrams/deployment.png "Vista de despliegue")

Despliegue local en un clúster k8s (p. ej., minikube/kind). 
- Acceso del usuario: el User consume las APIs vía HTTP a través de los Services de las apps.
- Patrón por dominio (users, posts, routes, offers):
  - App: contenedor Docker (*_app) ejecutado en k8s y expuesto por un Service.
  - Base de datos: contenedor (*_db) accesible mediante su Service interno.
  - Persistencia: volumen dedicado para la BD (PVC/PV) para evitar pérdida de datos al reiniciar pods.
- Comunicación: cada app se conecta solo a su BD vía el Service correspondiente (sin acceso cruzado).
- Operación: componentes aislados y escalables de forma independiente.

## Vista de redes

![Vista de redes](./diagrams/networks.png "Vista de redes")

K8s con cuatro dominios lógicos/“networks”: users, posts, routes, offers.
- Exposición externa: cada app se publica vía Service NodePort; el usuario accede por Internet → NodePort → *-app-service (HTTP :80) → pod *_app.
- Acceso a datos: la app se conecta a su propia BD vía ClusterIP *-db-service (:5432) → pod *_db. No hay acceso cruzado entre bases ni entre dominios.
- Aislamiento y escalabilidad: cada dominio puede escalarse y desplegarse de forma independiente manteniendo propiedad de datos por servicio.

## Vista de información

![Vista de información](./diagrams/entities.png "Vista de información")

Modelo lógico de datos para la primera iteración. Muestra entidades clave, atributos y relaciones.

## Vista de desarollo 

Se opta por utilizar una estructura similar a las 4 aplicaciones. Tomando como base la arquitectura hexagonal (aka. Puertos y adaptadores) se definen las carpetas `domain`, `adapters` y `entrypoints`. En la primera carpera se almacenaran las clases del dominio, los puertos y los casos de uso, mientras que en la segunda y tercera carpeta irán respectivamente los adaptadores (implementaciones de los puertos) y los puntos de entrada a la aplicación, la API REST. 

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

| Tecnología      | Descripción | Desarrollo, ejecución, pruebas o despliegue |
|-----------------|-------------|---------------------------------------------|
| Poetry          | Manejador de dependencias y empaquetado para proyectos en Python. Cada aplicación lo utilizo para manejar las dependencias. | Desarrollo |
| FastAPI         | Framework moderno y rápido para construir APIs con Python. Cada una de las aplicaciones esta desarrollado con esto. | Desarrollo |
| pytest          | Framework de pruebas para Python. Todas las aplicaciones se probaron con este framework. | Pruebas |
| PostgreSQL      | Base de datos relacional. En principio se desarrollaron todas las aplicaciones para conectarse a una base de datos de este tipo. | Ejecución |
| PlantUML        | Herramienta para generar diagramas a partir de texto. | Desarrollo |
| Postman         | Se utilizó para realizar las pruebas de la API con las colecciones ya definidas. | Pruebas |
| Docker          | Plataforma de contenedores para empaquetar y ejecutar aplicaciones. Todas las aplicaciones se empaquetaron con esto. | Ejecución |
| Minikube        | Herramienta para correr Kubernetes en local. | Despliegue |
| GitHub Actions  | Servicio de CI/CD integrado en GitHub. Para el proyecto solo se utilizo para integración continua: linter y la ejecución de las pruebas. Además, se utilizaron en los evaluadores. | Despliegue |

