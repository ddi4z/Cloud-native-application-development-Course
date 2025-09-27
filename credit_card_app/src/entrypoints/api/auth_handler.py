import os
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security_scheme = HTTPBearer()
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL")
if not USERS_SERVICE_URL:
    raise RuntimeError("La variable de entorno USERS_SERVICE_URL no está configurada.")

async def get_current_user_data(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """
    Valida el token llamando al endpoint /users/me del servicio de usuarios.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No hay token en la solicitud."
        )
    
    token = credentials.credentials
    
    # Hacemos una llamada HTTP al servicio de usuarios para validar el token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Si el servicio de usuarios dice que el token es válido (200 OK)
            if response.status_code == 200:
                user_data = response.json()
                # Retornamos los datos que necesitamos para el resto de la app
                return {"user_id": user_data.get("id"), "user_email": user_data.get("email")}
            
            # Si el token es inválido o expiró
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="El token no es válido o está vencido."
                )
            
            # Si el token no está presente (aunque ya lo validamos antes)
            elif response.status_code == 403:
                 raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token no encontrado en la solicitud."
                )
            
            # Para cualquier otro error del servicio de usuarios
            else:
                raise HTTPException(status_code=response.status_code, detail="Error al validar el usuario.")

        except httpx.RequestError:
            # Si no se puede comunicar con el servicio de usuarios
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de autenticación no está disponible."
            )