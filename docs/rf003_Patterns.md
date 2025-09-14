| Requerimiento | RF-003 – Crear publicación |
|---|---|
| Patrón utilizado | Orquestador de servicios  |
| Justificación | El orquestador (**rf003_app**) centraliza el flujo: valida autenticación/fechas, consulta/crea el trayecto en **routes_app**, verifica duplicidad en **posts_app** y finalmente crea la publicación, todo a través de APIs internas. Esto **reduce acoplamiento** entre dominios y concentra la lógica de proceso en un solo punto. Se complementa con **idempotencia** (cabecera Idempotency-Key) y **restricciones únicas** en BD para evitar duplicados, y con **transacciones locales** en cada servicio para mantener consistencia. |
| Atributos de calidad favorecidos | Mantenibilidad, Cohesión del flujo, Trazabilidad/Observabilidad, Reusabilidad, Seguridad (autorización consistente), Evolutividad |
| Atributos de calidad desfavorecidos | Latencia (salto extra por el orquestador), Complejidad operativa, Riesgo de cuello de botella/punto único si no escala en HA, Mayor superficie de fallos en cadenas remotas |
| Componentes involucrados | Ingress (ingress), RF003 App (rf003_app), Users Service (users_app), Routes Service (routes_app), Posts Service (posts_app), PostgreSQL RDS (platform_db) |
