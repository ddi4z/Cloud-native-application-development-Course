from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse

from src.assembly import (
    build_count_post_use_case,
    build_create_post_use_case,
    build_delete_post_use_case,
    build_filter_post_use_case,
    build_query_post_use_case,
    build_reset_post_use_case,
)
from src.domain.models.post_creation_request import PostCreationRequest
from src.domain.models.posts import Post
from src.domain.use_cases.base_use_case import BaseUseCase
from src.errors import (
    InvalidCredentialsError,
    InvalidExpirationDate,
    MissingIdError,
    MissingPostInformationError,
    PostNotFoundError,
)

router = APIRouter(prefix="/posts")


# 6. Consulta de salud del servicio
@router.get("/ping", response_class=PlainTextResponse)
def health_check():
    """Healthcheck endpoint."""
    return "pong"


# 5. Consultar cantidad de entidades
@router.get("/count")
def get_posts_count(use_case: BaseUseCase = Depends(build_count_post_use_case)):
    """
    Retrieve the total number of post entities stored in the database.
    All attributes in the response are required.
    """
    return JSONResponse(content={"count": use_case.execute()}, status_code=200)


# 1. Creación de posts
@router.post("", status_code=201)
def create_post(
    post_dto: PostCreationRequest,
    use_case: BaseUseCase = Depends(build_create_post_use_case),
):
    """
    Create a new Post.

    RouteId: Id of the route needed. UUID format.
    ExpireAt: datetime, ISO format. Needs to be in the future
    userId: id of user owning the post. UUID format.


    Returns the created post id, userId and createdAt
    """
    try:
        created_post = use_case.execute(post_dto)
        return {
            "id": created_post.id,
            "userId": created_post.userId,
            "createdAt": created_post.createdAt.isoformat(timespec="seconds"),
        }
    except InvalidExpirationDate:
        return JSONResponse(
            content={"msg": "La fecha expiración no es válida"}, status_code=412
        )
    except InvalidCredentialsError:
        return Response(status_code=400)
    except MissingPostInformationError:
        return Response(status_code=400)


# 2. Filter posts
@router.get("")
def filter_post(
    expire: Optional[bool] = Query(None, description="true=expired, false=not expired"),
    route: Optional[UUID] = Query(None, description="route id"),
    owner: Optional[UUID] = Query(None, description="owner/user id"),
    use_case: BaseUseCase = Depends(build_filter_post_use_case),
):
    """
    Filters all posts matching certain criteria.
    Accepts:
        expires: Bool; if post if expired (True) or not (False)
        routeid: UUID; id of route needed
        owner: UUID; id of user who owns post
    Returns:
        PostList: List; list of posts matching certain criteria. If no parameter is given, will return all posts
    """
    posts = use_case.execute(expire=expire, route=route, owner=owner)

    result = [
        {
            "id": str(post.id),
            "routeId": str(post.routeId) if getattr(post, "routeId", None) else None,
            "userId": str(post.userId) if getattr(post, "userId", None) else None,
            "expireAt": (
                post.expireAt.isoformat(timespec="seconds")
                if isinstance(post.expireAt, datetime)
                else post.expireAt
            ),
            "createdAt": (
                post.createdAt.isoformat(timespec="seconds")
                if isinstance(post.createdAt, datetime)
                else post.createdAt
            ),
        }
        for post in posts
    ]

    return result


# 3. Consultar una publicación
@router.get("/{id}")
def query_post(
    id: str,
    use_case: BaseUseCase = Depends(build_query_post_use_case),
):
    """
      Get information from a specific post, using its id
      Accepts:
          id: UUID
      Returns:
          JSON with all the information on the post:
            {
            "id": id de la publicación,
            "routeId": id del trayecto,
            "userId": id del usuario dueño de la publicación,
            "expireAt": fecha y hora máxima en que se recibirán ofertas en formato ISO,
            "createdAt": fecha y hora de creación de la publicación en formato ISO
    }
    """
    try:
        post = use_case.execute(id)
        return JSONResponse(
            content=jsonable_encoder(
                {
                    "id": post.id,
                    "routeId": post.routeId,
                    "userId": post.userId,
                    "expireAt": post.expireAt,
                    "createdAt": post.createdAt,
                }
            ),
            status_code=200,
        )

    except InvalidCredentialsError:
        return Response(status_code=400, content="InvalidCredentials")
    except PostNotFoundError:
        return Response(status_code=404, content="PostNotFound")


# 4. Consultar información del usuario
@router.delete("/{id}")
def delete_post(
    id: str,
    use_case: BaseUseCase = Depends(build_delete_post_use_case),
):
    """
    delete post matching a given id
    Accepts:
        id: postId that want to delete from database
    Returns:
        JSON: {
            "msg":"la publicación fue eliminada"
        }
    """
    try:
        use_case.execute(id)
        return JSONResponse(
            content={"msg": "la publicación fue eliminada"}, status_code=200
        )
    except PostNotFoundError as err:
        return Response(status_code=404)
    except InvalidCredentialsError as err:
        return Response(status_code=400)


# 7. Restablecer base de datos
@router.post("/reset")
def reset_users_database(use_case: BaseUseCase = Depends(build_reset_post_use_case)):
    """
    Delete all user data from the database.
    All attributes in the response are required.
    """
    use_case.execute()
    return JSONResponse(
        content={"msg": "Todos los datos fueron eliminados"}, status_code=200
    )
