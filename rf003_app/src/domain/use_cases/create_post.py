from datetime import datetime, timezone
from uuid import UUID
from src.domain.use_cases.base_use_case import BaseUseCase

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort

from src.domain.models.models import (UserInput, RouteCreateInput, PublicationResponse,PublicationResponseData, CreatePost, RouteDetails, CreatedPost)

from src.errors import ValidationError, InvalidTokenError, NoTokenError, InvalidRouteDatesError, InvalidExpiredAtError, ConflictError, ServiceCommunicationError




class CreatePostUseCase(BaseUseCase):
    """
    Orchestrator use case for creating a post. It communicates with other microservices
    to create the post in the system.
    """
    

    def __init__(
        self,
        users_client: UsersPort,
        routes_client: RoutesPort,
        posts_client: PostsPort,
    ):
        super().__init__()
        self.users_client = users_client
        self.posts_client = posts_client
        self.routes_client = routes_client


    async def execute(self, token:str, input_dto: UserInput):
        """
        Executes the process of creating a post by calling the microservice responsible
        for actually creating the post.
        
        :param user_id: ID of the user creating the post
        :param content: Content of the post to be created
        :return: Response from the post creation service
        """

        self.logger.info("[CREATE_POST_USE_CASE] pinging USERS_APP")
        await self.users_client.ping()
        self.logger.info("[CREATE_POST_USE_CASE] USERS_APP is up")

        self.logger.info("[CREATE_POST_USE_CASE] pinging ROUTES_APP")
        await self.routes_client.ping()
        self.logger.info("[CREATE_POST_USE_CASE] ROUTES_APP is up")

        self.logger.info("[CREATE_POST_USE_CASE] pinging POSTS_APP")
        await self.posts_client.ping()
        self.logger.info("[CREATE_POST_USE_CASE] POSTS_APP is up")
        
        # Validate user input is complete
        if input_dto.flightId is None or input_dto.expireAt is None or input_dto.plannedEndDate is None \
        or input_dto.plannedEndDate is None or input_dto.origin is None or input_dto.destiny is None or input_dto.bagCost is None:
            raise ValidationError('Inputs faltantes')
        
        # Validate dates are okay
            # aux variables
        current_date = datetime.now(timezone.utc)
        start_date_user_input = datetime.fromisoformat(input_dto.plannedStartDate)
        expire_date_user_input = datetime.fromisoformat(input_dto.expireAt)
        end_date_user_input = datetime.fromisoformat(input_dto.plannedEndDate) 
            
        # PlannedStartDate is in the future                        
        if start_date_user_input <= current_date:
            self.logger.error("[CREATE_POST_USE_CASE] invalid start date")
            raise InvalidRouteDatesError('la fecha de inicio debe estar en el futuro.')

        # PlannedEndDate must be after PlannedStartDate
        if end_date_user_input <= start_date_user_input:
            self.logger.error("[CREATE_POST_USE_CASE] invalid end date")
            raise InvalidRouteDatesError('La fecha de fin debe ser posterior a la fecha de inicio.')

        # Expire date between current date and start date
        if not (current_date < expire_date_user_input <= start_date_user_input):
            self.logger.error("[CREATE_POST_USE_CASE] invalid expiration date")
            raise InvalidExpiredAtError('La fecha de expiración debe ser posterior a fecha actual y anterior a comienzo viaje.')
        
        # Check for token
        if token is None:
            self.logger.error("[CREATE_POST_USE_CASE] missing token")
            raise NoTokenError('Token no está en la solicitud')
              
        # Validate user
        current_user = await self.users_client.get_user_from_token(token=token)

        if current_user is None:
            self.logger.error("[CREATE_POST_USE_CASE] unauthorized user")
            raise InvalidTokenError('Usuario no autorizado')
        
        self.logger.info(f"[CREATE_POST_USE_CASE] user validated: {current_user}")

        # Validate if provided route already exists
        route_search = await self.routes_client.find_route_by_flight_id(flightId=input_dto.flightId)

        # Check if there is already route, create if not, get id for any case
        if route_search is None:
            route_to_create = RouteCreateInput(
                flightId = input_dto.flightId,
                sourceAirportCode = input_dto.origin.airportCode,
                sourceCountry = input_dto.origin.country,
                destinyAirportCode = input_dto.destiny.airportCode,
                destinyCountry = input_dto.destiny.country,
                bagCost = input_dto.bagCost,
                plannedStartDate = input_dto.plannedStartDate,
                plannedEndDate = input_dto.plannedEndDate
            )
            self.logger.info(f"[CREATE_POST_USE_CASE] route didn't previously exist")

            route_created = await self.routes_client.create_route(route_dto=route_to_create)
            if route_created is None:
                self.logger.error("[CREATE_POST_USE_CASE] Failed to create route in Routes service")
                raise ServiceCommunicationError("No se pudo crear el trayecto en el servicio de rutas.")

            route_id = route_created.id
            route = route_created
        
        else:
            self.logger.info(f"[CREATE_POST_USE_CASE] route already existed")

            route_id = route_search.id
            route = route_search

        # Check if already a post for that route_id
        post = await self.posts_client.get_post_from_userid_route_id(user_id=current_user.id, route_id=route_id)

        if post:
            self.logger.error("[CREATE_POST_USE_CASE] post already exists")
            raise ConflictError('Usuario ya tiene una publicación para este trayecto')


        # crear post
        new_post_creation_request = CreatePost(
            routeId = UUID(route_id),
            expireAt = input_dto.expireAt,
            userId = UUID(current_user.id),
        )

        created_post = await self.posts_client.create_post(new_post_creation_request)

        if created_post is None:
            self.logger.error("[CREATE_POST_USE_CASE] Failed to create post in Posts service")
            raise ServiceCommunicationError("No se pudo crear la publicación en el servicio de posts.")

        self.logger.info(f"[CREATE_POST_USE_CASE] post created")

        return created_post, input_dto.expireAt, route.id, route.createdAt