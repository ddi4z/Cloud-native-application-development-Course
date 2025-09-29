import sys
from fastapi import APIRouter, Depends, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.assembly import (
    build_authenticate_user_use_case,
    build_create_user_with_verification_use_case,
    build_get_current_user_use_case,
    build_get_users_count_use_case,
    build_reset_users_use_case,
    build_update_user_status_use_case,
    build_update_user_use_case,
)
from src.domain.models.auth_request import AuthRequest
from src.domain.models.user_callback_request import UserCallbackRequest
from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_update_request import UserUpdateRequest
from src.domain.use_cases.base_use_case import BaseUseCase
from src.errors import (
    InvalidCredentialsError,
    InvalidTokenError,
    MissingTokenError,
    MissingUserInformationError,
    UnauthorizedUserStatusError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

router = APIRouter(prefix="/users")


# 1. Creación de usuarios
@router.post("/", status_code=201)
def create_user(
    user_dto: UserCreationRequest,
    use_case: BaseUseCase = Depends(build_create_user_with_verification_use_case),
):
    """
    Create a new user.

    The username and email must be unique.
    Returns the created user with ID and createdAt timestamp.
    """
    print(">>> Entrando a crear usuario", flush=True, file=sys.stdout)
    try:
        created_user = use_case.execute(user_dto)
        return {
            "id": created_user.id,
            "createdAt": created_user.createdAt.isoformat(timespec="seconds"),
        }
    except UserAlreadyExistsError:
        return Response(status_code=412)
    except MissingUserInformationError:
        return Response(status_code=400)


# 2. Actualización de usuarios
@router.patch("/{user_id}")
def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    use_case: BaseUseCase = Depends(build_update_user_use_case),
):
    """
    Updates a user's data.
    Only the received fields will be modified.
    Allowed fields: fullName, phoneNumber, dni, status.
    """
    try:
        use_case.execute(user_id, update_data)
        return JSONResponse(
            content={"msg": "el usuario ha sido actualizado"}, status_code=200
        )
    except UserNotFoundError:
        return Response(status_code=404)
    except MissingUserInformationError:
        return Response(status_code=400)


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
        user = use_case.execute(credentials.username, credentials.password)
        return JSONResponse(
            content=jsonable_encoder(
                {"id": user.id, "token": user.token, "expireAt": user.expireAt}
            ),
            status_code=200,
        )
    except InvalidCredentialsError:
        return Response(status_code=404)
    except MissingUserInformationError:
        return Response(status_code=400)
    except UnauthorizedUserStatusError:
        return Response(status_code=401)


# 4. Consultar información del usuario
security = HTTPBearer()


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    use_case: BaseUseCase = Depends(build_get_current_user_use_case),
):
    """
    Retrieve the authenticated user's information based on the Bearer token.
    All attributes are mandatory in the response.
    """
    token = credentials.credentials  # <-- Aquí obtenemos el token del Bearer
    print(token)

    try:
        user_data = use_case.execute(token)
        return JSONResponse(
            content={
                "id": user_data.id,
                "username": user_data.username,
                "email": user_data.email,
                "fullName": user_data.fullName,
                "dni": user_data.dni,
                "phoneNumber": user_data.phoneNumber,
                "status": user_data.status,
            },
            status_code=200,
        )
    except MissingTokenError as err:
        return Response(status_code=403)
    except InvalidTokenError as err:
        return Response(status_code=401)


# 5. Consultar cantidad de entidades
@router.get("/count")
def get_users_count(use_case: BaseUseCase = Depends(build_get_users_count_use_case)):
    """
    Retrieve the total number of user entities stored in the database.
    All attributes in the response are required.
    """
    return JSONResponse(content={"count": use_case.execute()}, status_code=200)


# 6. Consulta de salud del servicio
@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"


# 7. Restablecer base de datos
@router.post("/reset")
def reset_users_database(use_case: BaseUseCase = Depends(build_reset_users_use_case)):
    """
    Delete all user data from the database.
    All attributes in the response are required.
    """
    use_case.execute()
    return JSONResponse(
        content={"msg": "Todos los datos fueron eliminados"}, status_code=200
    )


@router.patch("/status/{user_id}", status_code=201)
def update_user_status(
    user_id: str,
    user_dto: UserCallbackRequest,
    use_case: BaseUseCase = Depends(build_update_user_status_use_case),
):
    """
    Update user status based on external callback data.
    Sends an email notification after updating the user.
    """
    try:
        updated_user = use_case.execute(user_id, user_dto)
        return {
            "id": updated_user.id,
            "updatedAt": updated_user.updatedAt.isoformat(timespec="seconds"),
            "status": updated_user.status,
        }
    except UserAlreadyExistsError:
        return Response(status_code=412)
    except MissingUserInformationError:
        return Response(status_code=400)
