## Vista de componentes
  
![Vista de componentes](./diagrams/components.png "Vista de componentes")

Arquitectura por servicios con propiedad de datos por dominio y acoplamiento bajo, enfocada en cubrir funcionalidades esenciales de la segunda entrega.
## Descripción del sistema

### Actor (líneas punteadas)
El **User** interactúa vía **API REST** exclusivamente con los **nuevos servicios**:
- **RF-003 Crear Publicación** → `POST rf003/posts`
- **RF-004 Crear Ofertas** → `POST 	/rf004/posts/{id}/offers`
- **RF-005 Consultar Publicaciones** → `GET /rf005/posts/{id}`  

Autenticación por Bearer Token.  
Los servicios de dominio se consumen de forma interna por los RF-003-005.

### Servicios (cajas rosadas)
- **Orquestadores/fachada:** `rf003_app`, `rf004_app`, `rf005_app` (exponen las APIs al usuario).  
- **Servicios de dominio:** `users_app`, `routes_app`, `posts_app`, `offers_app` (APIs internas).  

Todos son **desplegables de forma independiente** y se comunican entre sí vía **HTTP/JSON**  
(sin acceso directo a datos ajenos).

### Persistencia (cilindro azul)
- **Una sola base de datos** **PostgreSQL en la nube** (en AWS).  
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
| Consideraciones de diseño  | **Concurrencia:** manejar carreras entre dos creaciones simultáneas (bloqueo optimista/únicos a nivel de posts).<br>**Fechas y zonas horarias:** comparar en **UTC**, definir claramente inclusiones (`expiración ≤ inicio`).<br>**Errores y contratos:** 400 validación, 401/403 autenticación, 412 conflicto y validaciones de inputs.<br>**Observabilidad:** Observabilidad:** `X-Request-Id`, trazas con logs estructurados y métricas de intentos/éxitos/fallos. ||
| Integraciones              | **Auth/Usuarios** (`users_app` o gateway): Bearer token; validar identidad y obtener `user_id` (sincronía).<br>**Rutas** (`routes_app`): `GET /routes?…` para buscar; `POST /routes` para crear cuando no exista (JSON/HTTP).<br>**Publicaciones** (`posts_app`): `GET /posts?owner={userId}&route={routeId}` para verificar duplicados; `POST /posts` para crear (JSON/HTTP).<br>**Comunicación:** síncrona REST, *timeouts* |           |

### Componente RF-004

| Componente                 | RF-004                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Código/Id del componente | RF-004                                                            |
| Tipo                  | Servicio orquestador (use case de dominio) expuesto por API HTTP/REST                                                                       |
| Responsabilidad       | 1) Recibir datos de la oferta y el **id de la publicación**.<br>2) Autenticar al usuario (solo sesión válida).<br>3) Validar que la publicación **existe**.<br>4) Verificar que la publicación **no haya expirado**.<br>5) Impedir que el usuario **oferte sobre su propia publicación**.<br>6) **Calcular el score** (utilidad) de la oferta.<br>7) Crear la oferta **asociándola** al usuario autenticado y a la publicación indicada, persistiendo el score.<br>8) Asegurar **consistencia** al finalizar (éxito o error). |
| Consideraciones de diseño | **Concurrencia:** varias ofertas pueden llegar simultáneamente; usar transacciones y niveles de aislamiento adecuados.<br>**Transacciones/Consistencia:** operaciones atómicas (leer publicación → calcular score → crear oferta). Si falla el cálculo del score o la persistencia, **rollback** completo.<br>**Fechas y zonas horarias:** validar expiración en **UTC** contra la hora del servidor.<br>**Seguridad:** 400 si input está incopmpleto; 401/403 si no hay autenticación o es incorrecta; 404 si la publicación no existe; 412 si la publicación está expirada o es del mismo usuario; 503 si falla comunicación con servidor.<br>**Observabilidad:** `X-Request-Id`, métricas de intentos/éxitos/fallos, trazas distribuidas. |
| Integraciones         | **Auth/Usuarios** (gateway o `users_app`): Bearer token para identidad y `user_id` (síncrono).<br>**Publicaciones** (`posts_app`): `GET /posts/{postId}` para verificar existencia/expiración y dueño (JSON/HTTP).<br>**Ofertas** (`offers_app`): `POST /offers` para persistir la oferta (JSON/HTTP).<br>**Scores** (`scores_app`): `POST /scores/offers` (o equivalente) para calcular la utilidad antes de persistir; *timeouts* y reintentos con backoff; propagar `X-Request-Id`/`Idempotency-Key`. |

### RF-005

| Componente                 | RF-005                                                                                      |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Código/Id del componente** | RF-005                                      |
| **Tipo**                  | Servicio orquestador de lectura (consulta compuesta) expuesto por API HTTP/REST                                                               |
| **Responsabilidad**       | 1) Recibir el **id de la publicación**.<br>2) Autenticar y **autorizar**: solo el **propietario** puede consultar.<br>3) Obtener la publicación y su **trayecto** asociado.<br>4) Listar **ofertas** de la publicación.<br>5) Obtener/adjuntar la **utilidad (score)** de cada oferta y **ordenar** de forma **descendente** por score (los `null` al final).<br>6) Si la utilidad no se puede calcular/recuperar temporalmente, devolver `score: null` para esa oferta.<br>7) Responder con un objeto unificado: publicación + trayecto + ofertas (cada una con su score). |
| **Consideraciones de diseño** | **Concurrencia:** varias ofertas pueden llegar simultáneamente; usar transacciones y niveles de aislamiento adecuados.<br>**Transacciones/Consistencia:** operaciones atómicas (leer publicación → calcular score → crear oferta). Si falla el cálculo del score o la persistencia, **rollback** completo.<br>**Fechas y zonas horarias:** validar expiración en **UTC** contra la hora del servidor.<br>**Seguridad:** 401/403 si no hay autenticación; 404 si la publicación no existe; 503 si hay error de comunicación con el servidor. **Observabilidad:** `X-Request-Id`, métricas de intentos/éxitos/fallos, trazas distribuidas. |
| **Integraciones**         | **Auth/Usuarios** (gateway o `users_app`): Bearer token para identidad y `user_id` (síncrono).<br>**Publicaciones** (`posts_app`): `GET /posts/{postId}` para verificar existencia/expiración y dueño (JSON/HTTP).<br>**Ofertas** (`offers_app`): `POST /offers` para persistir la oferta (JSON/HTTP).<br>**Scores** (`scores_app`): `POST /scores/offers` (o equivalente) para calcular la utilidad antes de persistir; *timeouts* y reintentos con backoff; propagar `X-Request-Id`/`Idempotency-Key`. |
