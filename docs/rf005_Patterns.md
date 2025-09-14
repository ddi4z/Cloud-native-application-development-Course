| Requerimiento | RF-005 – Consultar publicaciones |
|---|---|
| Patrón utilizado | Orquestador de servicios |
| Justificación | **rf005_app** orquesta la creación: valida **autenticación** y que el usuario **no oferte sobre su propia publicación**; verifica en **posts_app** que la publicación **existe** y **no ha expirado**; **calcula el score** en **scores_app**; y crea la **oferta** en **offers_app**. Usa **Idempotency-Key** y **restricciones únicas** (p. ej., `(owner_id, post_id)`) para evitar duplicados en reintentos. Al no haber transacción distribuida, se adopta **saga orquestada** con pasos y (si aplica) **compensaciones** (p. ej., invalidar un score preliminar si falla la creación de la oferta). |
| Atributos de calidad favorecidos | Integridad de negocio, Consistencia local por dominio, Mantenibilidad, Observabilidad, Seguridad (reglas y ownership), Evolutividad |
| Atributos de calidad desfavorecidos | Latencia (llamadas encadenadas), Complejidad operativa, Mayor superficie de fallo (dependencia de servicios remotos), Posible compensación si un paso intermedio falla |
| Componentes involucrados | Ingress (ingress), RF005 App (rf005_app), Users Service (users_app), Posts Service (posts_app), Offers Service (offers_app), Scores Service (scores_app), PostgreSQL RDS (platform_db) |
