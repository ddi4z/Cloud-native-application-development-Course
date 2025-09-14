| Requerimiento | RF-004 – Crear ofertas |
|---|---|
| Patrón utilizado | Orquestador |
| Justificación | **rf004_app** centraliza una **consulta compuesta**: autentica/autoriza (solo dueño), obtiene la **publicación** en **posts_app**, el **trayecto** en **routes_app**, las **ofertas** en **offers_app** y los **scores** en **scores_app**; luego ordena por score **descendente**. Para **resiliencia**, aplica *timeouts* y **fallback**: si `scores_app` está indisponible, retorna `score: null` sin fallar toda la respuesta. Evita *joins* cruzados y mantiene **bajo acoplamiento** entre dominios al componer por API. |
| Atributos de calidad favorecidos | Resiliencia, Disponibilidad percibida, Mantenibilidad, Cohesión del flujo, Observabilidad/Trazabilidad, Seguridad (autorización consistente) |
| Atributos de calidad desfavorecidos | Latencia (múltiples hops), Complejidad del orquestador, Inconsistencia temporal de lectura (no atómico), Dependencia parcial del score para el orden |
| Componentes involucrados | Ingress (ingress), RF004 App (rf004_app), Users Service (users_app), Posts Service (posts_app), Offers Service (offers_app), Routes Service (routes_app), Scores Service (scores_app), PostgreSQL RDS (platform_db) |
