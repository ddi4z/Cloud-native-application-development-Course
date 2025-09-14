# RF-004 - Crear oferta

## Secuencia resumida

1. `rf004_app` recibe `auth_token`, `post_id` y el objeto `offer`.
2. Realiza **ping** de *readiness* a `USERS_APP`, `OFFERS_APP` y `POSTS_APP` (logs).
3. Valida que `offer.description`, `offer.size`, `offer.fragile` y `offer.offer` **no sean None**.
4. Autentica al usuario: `user_validation.validate_token_and_get_user(token)` → `user`.
5. Valida la publicación: `post_validation.validate_and_get_post(postId)` → `post`.
6. Verifica que la publicación **no esté expirada** (`post.expireAt` vs `now(UTC)`).
7. Enforce regla: el usuario **no puede** ofertar sobre su **propia** publicación (`post.userId != user.id`).
8. **Crea la oferta**: `create_offer.create_offer(offer, userId=user.id, postId=post_id)` → `created_offer`.
9. Obtiene `bagCost` del trayecto: `find_bagcost.get_bagcost(post.routeId)` (si `None`, usar `0`).
10. **Calcula el score**: `score_calculation.calculate_score(Score(...))` (log del resultado).
11. **Responde** con `created_offer` (HTTP **201 Created** sugerido).


---

## Entradas
- `auth_token` (Bearer, requerido).
- `post_id` (string, requerido).
- `offer` (objeto con **description**, **size**, **fragile**, **offer**; todos obligatorios).

---

## Flujo principal (éxito)
1. **Ping servicios** para *readiness* (logs): `USERS_APP`, `OFFERS_APP`, `POSTS_APP`.
2. **Validar entrada de la oferta.**  
   Si falta `description|size|fragile|offer` → error.
3. **Autenticar usuario.**  
   `user_validation.validate_token_and_get_user(token)` → `user`.  
4. **Validar publicación.**  
   `post_validation.validate_and_get_post(postId)` → `post`.
5. **Verificar vigencia de la publicación.**  
   Si `post.expireAt` < `now(UTC)` → error.
6. **Regla de negocio:** el autor **no** puede ofertar en su propia publicación.  
   Si `post.userId == user.id` → error.
7. **Crear oferta.**  
   `create_offer.create_offer(offer, userId=user.id, postId=post_id)` → `created_offer`.  
   > La creación de la oferta sucede **antes** del cálculo de score.
8. **Calcular score.**  
   - `bagCost = find_bagcost.get_bagcost(post.routeId)` (si `None` → usar `0`).  
   - `score_calculation.calculate_score(Score(...))` (log de resultado).
9. **Responder.**  
   Retornar `created_offer`. (HTTP **201 Created** sugerido).

---

## Excepciones y manejo de errores

| Paso | Condición | Excepción (del código) | HTTP sugerido |
|---|---|---|---|
| 2 | Props de oferta `None` | `InvalidOfferInputError` | 400 |
| 3 | Token inválido/sin usuario | `UnauthorizedError` | 401 |
| 4 | Token no está en solicitud | `UnauthorizedError` | 403 |
| 5 | Publicación no existe | `PostNotFoundError` | 404 | 
| 6 | Publicación expirada | `PostExpiredError` | 412 |
| 7 | Oferta sobre propia publicación | `OfferOnOwnPostError` | 412 |
| 8 | Falla al crear oferta | (excepción del adapter) | 503 |
| 9 | Falla al calcular score | (excepción del adapter) | 503 |

**Casos límites cubiertos por la implementación:**
- `bagCost` no disponible → se usa `0` para el cálculo del score.
- Comparación de expiración usa `datetime.now(timezone.utc)` + `fromisoformat(post.expireAt)`.

---

## Observabilidad y reglas técnicas
- **Logs** detallados por paso (`self.logger.info/error`).
- Pings de *readiness* previos a la orquestación (ayuda a diagnósticos).

---

## Respuesta (éxito)
- Objeto **`CreatedOffer`** (id y metadatos de la oferta creada).  
- HTTP **201 Created**.
