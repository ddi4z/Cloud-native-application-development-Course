## Vista de despliegue

![Vista de despliegue](./diagrams/deployment.png "Vista de despliegue")

> **Modelo de despliegue:** describe cómo los componentes funcionales (RF-003 - 007 y servicios de dominio `users/routes/posts/offers/scores`) se despliegan usando servicios de nube.

## Entorno
- Kubernetes en **AWS** (p. ej., **EKS**).
- Todas las imágenes se publican y se **extraen desde Amazon ECR**.
- Funciones de soporte (`poller`, `emails_app`) desplegadas como **AWS Lambda**.

## Acceso del usuario (entrada única)
Un **Ingress** (Nginx / AWS Load Balancer Controller + ALB) expone un punto HTTP(S) y enruta por **host/path** hacia:
- **RF-003 Crear Publicación** → `POST /posts` → **rf003-app-service**
- **RF-004 Ver publicación + ofertas** → `GET /posts/{id}/details` → **rf004-app-service**
- **RF-005 Crear oferta** → `POST /offers` → **rf005-app-service**
- **RF-006 Gestión de Tarjetas de Crédito** → `POST /credit-card/cards` → **credit-card-app-service**
- **RF-007 Webhook Verificación Usuario** → `POST /users/native/verify` → **users-app-service**
- **TrueNative** (servicio simulado externo) → `/native/*` → **native-app-service**

## Consumo directo de servicios de dominio (interno)
Además de ser llamados por los RF, los servicios de dominio  
(**users_app, routes_app, posts_app, offers_app, scores_app, credit_card_app**)  
pueden **exponer endpoints** para Backoffice/integraciones mediante:
- **ClusterIP Services** (DNS interno de k8s), y/o
- **Reglas adicionales en el mismo Ingress** con **restricciones** (mTLS, IP allowlist, autenticación).

Rutas internas típicas: `/users/*`, `/routes/*`, `/posts/*`, `/offers/*`, `/scores/*`, `/credit-card/*`.

## Patrón de despliegue por servicio
- **Pod** por servicio con **Docker** encapsulando la app (`*_app`) y un **Service** delante (ClusterIP).
- Servicios **RF**: `rf003_app`, `rf004_app`, `rf005_app`, `credit_card_app`.
- Servicios de **dominio**: `users_app`, `routes_app`, `posts_app`, `offers_app`, `scores_app`.
- **TrueNative**: desplegado en el mismo clúster para simular verificación de tarjetas y usuarios.
- **Funciones de soporte**: `polling` (verificación tarjetas, asíncrono) y `email_service` (envío de notificaciones) → AWS Lambda.

## Persistencia (única en la nube)
- **PostgreSQL en AWS (RDS)** como **única BD**: `platform_db`.
- Cada dominio **posee sus propias tablas/esquemas**:  
  - `users.*`, `routes.*`, `posts.*`, `offers.*`, `scores.*`, `credit_cards.*`.
- **Sin llaves foráneas cruzadas** ni *joins* entre dominios; coordinación vía **APIs** y colas/eventos.
- **Sin PVC/PV** de BD en el clúster (la BD es gestionada por RDS). Conexión mediante **Secrets**.

## Comunicación entre servicios
- **HTTP/JSON síncrono**:  
  - RF003 → `users_app`, `routes_app`, `posts_app`  
  - RF004 → `users_app`, `posts_app`, `offers_app`, `routes_app`, `scores_app`  
  - RF005 → `users_app`, `posts_app`, `offers_app`, `scores_app`  
  - RF006 → `credit_card_app` → `TrueNative` (tokenización); `polling_worker` → `TrueNative` (status)  
  - RF007 → `users_app` recibe callback de `TrueNative`  
- **Eventos/colas (asíncrono)**:  
  - `credit_card_app` → `SQS cc-verification-jobs` → `polling`  
  - `polling_worker` → `SQS email-notify` → `email_service`  
  - `users_app` (RF-007) → `SQS email-notify` → `emails_app`

## Operación y escalado
- **Aislamiento y escalado independiente** por servicio (HPA para Pods, concurrencia configurada en Lambda).
- **Rolling updates**, *readiness/liveness probes* para Pods.
- **NetworkPolicy** para tráfico Este–Oeste; **RBAC** e **IRSA**/credenciales mínimas para acceder a RDS/ECR/SQS/SES.
- **Observabilidad**: trazabilidad con `X-Request-Id`, métricas y trazas distribuidas; *timeouts* y *reintentos* con *backoff*.
- **Seguridad**: Bearer token en capa RF; secretos gestionados en Secrets Manager/K8s Secrets; validación de token secreto en callbacks de TrueNative.

## Idempotencia y consistencia
- Claves de idempotencia y **restricciones únicas** (p. ej., `(owner_id, route_id)` en publicaciones, `transactionIdentifier` en tarjetas).  
- Transacciones en RDS para **consistencia**.  
- Degradación controlada: si `scores_app` o `polling_worker` no responden, se retornan valores nulos o se reintenta vía cola.  

---

## Servicios cloud usados
- **Amazon EKS** – Orquestación Kubernetes (Pods, Services, HPA, RBAC).  
- **Ingress Controller** (Nginx / **AWS Load Balancer Controller** + **ALB**) – Entrada HTTP(S) y *routing* por host/path.  
- **Amazon ECR** – Registro de imágenes de contenedor (pull desde los Pods).  
- **Amazon RDS for PostgreSQL** – Base de datos única `platform_db`.  
- **AWS Lambda** – `polling_worker` y `email_service`.  
- **Amazon SQS** – Colas de verificación de tarjetas y notificaciones de email.  
- **Amazon SES** – Salida de correos electrónicos.  
- **AWS Secrets Manager / Kubernetes Secrets** – Gestión de credenciales y cadenas de conexión.  
- **AWS IAM / IRSA** – Permisos mínimos para Pods y Lambdas hacia servicios AWS (ECR, RDS, SQS, SES, Secrets).  
- **Amazon CloudWatch / Prometheus + Grafana** – Logs, métricas y trazas distribuidas.  
- **AWS Certificate Manager (ACM)** – Certificados TLS para el Ingress/ALB.  



# Vista de Redes
![Vista de redes](./diagrams/networks.png "Vista de despliegue")

- **K8s con dominios lógicos (“networks”):** `users`, `posts`, `routes`, `offers`, `scores`, `credit-cards` y una **capa de APIs expuestas** (`rf003`, `rf004`, `rf005`, `credit_card_app`).  
  Además, se despliega **TrueNative** como servicio externo simulado y dos funciones de soporte (`polling_worker`, `email_service`) que operan fuera del clúster (AWS Lambda).

- **Exposición externa:** **único Ingress** (Nginx/ALB). Flujo:  
  **Internet → Ingress → rf00x-app-service / credit-card-app-service / native-app-service (HTTP :80) → pod correspondiente → (interno) servicios de dominio**  
  (`users_app`, `routes_app`, `posts_app`, `offers_app`, `scores_app`, `credit_card_app`, todos como **ClusterIP**).  
  Para RF-007, **TrueNative** invoca el webhook en `users_app` vía Ingress.

- **Acceso a datos:** **una sola BD PostgreSQL (AWS RDS)** `platform_db`.  
  Cada servicio accede **solo a sus tablas/esquema** (p. ej., `users.*`, `routes.*`, `posts.*`, `offers.*`, `scores.*`, `credit_cards.*`).  
  **Sin llaves foráneas cruzadas ni joins** entre dominios; conexión mediante **Secrets**.  
  *(Se eliminan los pods `*_db` y sus NodePorts; RDS es gestionado fuera del clúster).*

- **Mensajería y soporte:**  
  - **Amazon SQS** conecta `credit_card_app` → `polling_worker` → `email_service`.  
  - `users_app` (RF-007) también publica eventos en la cola de email.  
  - **Amazon SES** entrega correos a los usuarios.  
  Estas funciones (`polling_worker`, `email_service`) corren como **AWS Lambda**, desacopladas del clúster.

- **Imágenes y nube:** Contenedores publicados en **Amazon ECR**; los Pods hacen *pull* con **IAM/IRSA**. El clúster corre en **EKS**.  
  Lambdas (`polling_worker`, `email_service`) pueden publicarse como imágenes en ECR o paquetes ZIP.

- **Aislamiento y escalabilidad:** cada servicio se **despliega y escala** de forma independiente (HPA en Pods, concurrencia configurada en Lambdas), manteniendo **propiedad de datos por dominio** y comunicación **HTTP/JSON** o **eventos en SQS** entre servicios.



# Vista de información
![Vista de despliegue](./diagrams/entities.png "Vista de despliegue")

Modelo lógico de datos para la tercera iteración. Muestra entidades clave, atributos y relaciones.
