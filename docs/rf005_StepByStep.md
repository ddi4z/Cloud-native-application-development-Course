# RF-005 — Consultar Publicaciones

## Secuencia resumida (texto)
1. `rf005_app` recibe `post_id` y `token`.
2. Llama a `users_client.get_user_from_token` y `posts_client.get_post_by_id`.
3. Si el token es inválido → `InvalidTokenError`; si el post no existe → `EntityNotFoundError`.
4. Verifica que `current_user.id == post.userId`; si no → `AuthorizationError`.
5. Obtiene `route` y `offers`.
6. Construye `OfferDetails` normalizando `size` y fijando `score=None`.
7. Retorna `PublicationResponse(data=...)` (200 OK).


---

## Entradas
- `post_id` (string, requerido)
- `token` (Bearer, requerido)

---

## Flujo principal (éxito)
1. **Autenticación y obtención de post** (try/except):
   - `users_client.get_user_from_token(token)` → `current_user`
   - `posts_client.get_post_by_id(post_id)` → `post`
2. **Autorización (owner-only):**  
   Si `current_user.id != post.userId` → error.
3. **Datos relacionados:**
   - `routes_client.get_route_by_id(post.routeId)` → `route`
   - `offers_client.get_offers_by_post_id(post.id)` → `offers`
4. **Normalización de ofertas:**
   - Para cada `o` en `offers`, construir `OfferDetails` con:
     - `size`: si viene como `"Enum.VALUE"`, usar `"VALUE"`
     - `score`: **`None`** (cálculo comentado)
5. **Respuesta:**  
   Construye `PublicationResponseData` con `post`, `route` y `offers` (sin ordenar por score), y lo envuelve en `PublicationResponse`.

---

## Excepciones y manejo

| Paso | Condición | Excepción (del código) | HTTP sugerido 
|---|---|---|---|
| 1 | Token inválido | `InvalidTokenError` | 401 |
| 1 | Post no existe | `EntityNotFoundError("La publicación no existe.")` | 404 |
| 2 | Usuario no es el dueño | `AuthorizationError` | 403 |
| 3 | Error de comunicación con servicios | `ServiceCommunicationError` | 503 |

---

## Respuesta (éxito)
- **`PublicationResponse`** con `data`:
  - `id`, `expireAt`, `createdAt`
  - `route` (`RouteDetails` con `flightId`, `origin/destiny`, `bagCost`, `plannedStartDate`, `plannedEndDate`)
  - `offers: List[OfferDetails]` con `score=None`
- **HTTP 200 OK**
