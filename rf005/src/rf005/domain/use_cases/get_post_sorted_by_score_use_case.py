from typing import List

from ..models.models import (
    PublicationResponse, PublicationResponseData, RouteDetails,
    OfferDetails, RouteOrigin, RouteDestiny, Offer, Route, OfferWithScore, Post
)
from ...errors import (
    AuthorizationError,
    ServiceCommunicationError,
    EntityNotFoundError,
    InvalidTokenError,
)
from ..ports.ports import (
    UsersClientPort,
    PostsClientPort,
    RoutesClientPort,
    OffersClientPort,
    ScoreClientPort,
)

class GetPostSortedByScoreUseCase:
    """Orquesta la obtención de todos los datos para el requerimiento RF-005."""

    def __init__(
        self,
        users_client: UsersClientPort,
        posts_client: PostsClientPort,
        routes_client: RoutesClientPort,
        offers_client: OffersClientPort,
        score_client: ScoreClientPort,
    ):
        self.users_client = users_client
        self.posts_client = posts_client
        self.routes_client = routes_client
        self.offers_client = offers_client
        self.score_client = score_client

    async def execute(self, post_id: str, token: str) -> PublicationResponse:
        # Autenticar usuario y obtener la publicación
        try:
            current_user = await self.users_client.get_user_from_token(token)
            post = await self.posts_client.get_post_by_id(post_id)
        except InvalidTokenError as e:
            raise e # error de token inválido
        except EntityNotFoundError:
            # Si el post no existe, lanzamos el error específico.
            raise EntityNotFoundError("La publicación no existe.")
        except ServiceCommunicationError as e:
            raise e # error de comunicación

        # Autorizar: Verificar si el usuario es el dueño de la publicación
        if current_user.id != post.userId:
            raise AuthorizationError("El usuario no tiene permiso para ver el contenido de esta publicación.")

        # Obtener datos relacionados (trayecto y ofertas)
        route = await self.routes_client.get_route_by_id(post.routeId)
        offers = await self.offers_client.get_offers_by_post_id(post.id)

        offers_details: List[OfferDetails] = []
        for o in offers:
            # Si size llega como "OfferSize.LARGE", normaliza a "LARGE"
            size_value = o.size.split(".")[-1] if isinstance(o.size, str) else o.size

            offers_details.append(OfferDetails(
                id=o.id,
                userId=o.userId,
                description=o.description,
                size=size_value,
                fragile=o.fragile,
                offer=o.offer,
                score=None,             
                createdAt=o.createdAt,
            ))

        # # Calcular score para cada oferta. Si falla, el score es None.
        # offers_with_score: List[OfferWithScore] = []
        # for offer in offers:
        #     try:
        #         score = self.score_client.calculate_score(offer, route)
        #         offer_with_score = OfferWithScore(**offer.model_dump(), score=score)
        #     except Exception:
        #         # Como lo requiere el enunciado, si el cálculo del score falla, se asigna None (null en JSON)
        #         offer_with_score = OfferWithScore(**offer.model_dump(), score=None)
        #     offers_with_score.append(offer_with_score)

        # # Ordenar ofertas por score (descendente), manejando los valores nulos.
        # offers_with_score.sort(key=lambda o: (o.score is not None, o.score), reverse=True)

        # Respuesta final usando los modelos de Pydantic
        response_data = PublicationResponseData(
            id=post.id,
            expireAt=post.expireAt,
            route=RouteDetails(
                id=route.id,
                flightId=route.flightId,
                origin=RouteOrigin(airportCode=route.sourceAirportCode, country=route.sourceCountry),
                destiny=RouteDestiny(airportCode=route.destinyAirportCode, country=route.destinyCountry),
                bagCost=route.bagCost,
            ),
            plannedStartDate=route.plannedStartDate,
            plannedEndDate=route.plannedEndDate,
            createdAt=post.createdAt,
            # offers=[OfferDetails(**o.model_dump()) for o in offers_with_score]
            offers=offers_details,
        )

        return PublicationResponse(data=response_data)