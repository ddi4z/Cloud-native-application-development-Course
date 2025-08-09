from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordBearer

from assembly import (
    build_create_user_use_case,
    build_update_user_use_case,
    build_authenticate_user_use_case,
    build_get_current_user_use_case,
    build_get_users_count_use_case,
    build_reset_users_use_case
)
from users_app.src.domain.models.auth_request import AuthRequest
from users_app.src.domain.models.user import User
from domain.use_cases.base_use_case import BaseUseCase
from errors import InvalidCredentialsError, InvalidTokenError, MissingTokenError, UserAlreadyExistsError, UserNotFoundError
from users_app.src.domain.models.user_update_request import UserUpdateRequest

router = APIRouter(prefix="/users")

# 1. Creación de usuarios
@router.post("/", response_model=User, status_code=201)
def create_user(user: User, use_case: BaseUseCase = Depends(build_create_user_use_case)):
    """
    Create a new user.

    The username and email must be unique.
    Returns the created user with ID and createdAt timestamp.
    """
    try:
        return use_case.execute(user)
    except UserAlreadyExistsError as err:
        raise HTTPException(status_code=412, detail=str(err))
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

# 2. Actualización de usuarios
@router.patch("/{user_id}")
def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    use_case: BaseUseCase = Depends(build_update_user_use_case),
):
    """
    Updates a user's data.
    Only the received fields will be modified.
    Allowed fields: fullName, phoneNumber, dni, status.
    """
    if not any([update_data.status, update_data.dni, update_data.fullName, update_data.phoneNumber]):
        raise HTTPException(status_code=400, detail="Debe enviar al menos un campo para actualizar.")

    try:
        use_case.execute(user_id, update_data.dict(exclude_none=True))
        return JSONResponse(content={"msg": "el usuario ha sido actualizado"}, status_code=200)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))


# 3. Generación de token
@router.post("/auth")
def generate_token(
    credentials: AuthRequest,
    use_case: BaseUseCase = Depends(build_authenticate_user_use_case),
):
    """
    Generate a new token for the user given valid username and password.
    All fields are mandatory.
    """
    try:
        token_data = use_case.execute(credentials.username, credentials.password)
        return JSONResponse(
            content={
                "id": token_data["id"],
                "token": token_data["token"],
                "expireAt": token_data["expireAt"]
            },
            status_code=200
        )
    except InvalidCredentialsError as err:
        raise HTTPException(status_code=404, detail=str(err))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/auth")

# 4. Consultar información del usuario
@router.get("/me")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    use_case: BaseUseCase = Depends(build_get_current_user_use_case),
):
    """
    Retrieve the authenticated user's information based on the provided token.
    All attributes are mandatory in the response.
    """
    try:
        user_data = use_case.execute(token)
        return JSONResponse(
            content={
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "fullName": user_data["fullName"],
                "dni": user_data["dni"],
                "phoneNumber": user_data["phoneNumber"],
                "status": user_data["status"]
            },
            status_code=200
        )
    except MissingTokenError as err:
        raise HTTPException(status_code=403, detail=str(err))
    except InvalidTokenError as err:
        raise HTTPException(status_code=401, detail=str(err))

# 5. Consultar cantidad de entidades
@router.get("/count")
def get_users_count(use_case: BaseUseCase = Depends(build_get_users_count_use_case)):
    """
    Retrieve the total number of user entities stored in the database.
    All attributes in the response are required.
    """
    return JSONResponse(
        content={
            "count": use_case.execute()
        },
        status_code=200
    )

# 6. Consulta de salud del servicio
@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"

# 7. Restablecer base de datos
def reset_users_database(use_case: BaseUseCase = Depends(build_reset_users_use_case)):
    """
    Delete all user data from the database.
    All attributes in the response are required.
    """
    use_case.execute()
    return JSONResponse(
        content={
            "msg": "Todos los datos fueron eliminados"
        },
        status_code=200
    )