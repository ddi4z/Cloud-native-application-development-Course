from datetime import datetime

from src.domain.use_cases.base_use_case import BaseUseCase

from src.domain.models.models import (UserInput, User, Route, Post, PublicationResponseData, CreatePost)

from errors import ValidationError, InvalidTokenError, NoTokenError, InvalidRouteDatesError, InvalidExpiredAtError, ConflictError, ServiceCommunicationError

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort


class CreatePostUseCase(BaseUseCase):
    """
    Orchestrator use case for creating a post. It communicates with other microservices
    to create the post in the system.
    """
    

    def __init__(
            self,
            users_client: UsersPort,
            posts_client: PostsPort,
            routes_client: RoutesPort,
    
    ):
        
        self.users_client = users_client
        self.posts_client = posts_client
        self.routes_client = routes_client  


    def _validate_post_creation(self, user_id: str, input_dto: UserInput):
        """Validates the post data against business rules."""
        current_date = datetime.now().date()
        try: 
            date_user_input = datetime.fromisoformat(input_dto.plannedStartDate)
        
        except ValidationError as e:
            raise e('La fecha debe estar en el formato correcto')
        
        if date_user_input <= current_date:
            raise InvalidRouteDatesError('la fecha de inicio debe estar en el futuro.')
        
        if current_date < input_dto.expireAt <= input_dto.plannedStartDate:
            raise InvalidExpiredAtError('La fecha de expiración debe ser posterior a fecha actual y anterior a comienzo viaje.')
        

    async def _validate_existing_post(self, user_id: str, input_dto: UserInput):
        """" Checks if user already has a post for same route"""
        existing_route = await self.routes_client.find_route_by_flightid(input_dto.flightId)

        if existing_route:
            existing_post = await self.posts_client.get_post_from_userid_route_id(user_id, existing_route.id)
            if existing_post:
                raise ConflictError("Ya existe una publicación para ese trayecto")


    async def execute(self, input_dto: UserInput, token:str) -> PublicationResponseData:
        """
        Executes the process of creating a post by calling the microservice responsible
        for actually creating the post.
        
        :param user_id: ID of the user creating the post
        :param content: Content of the post to be created
        :return: Response from the post creation service
        """

        # Autenticar al user
        try:
            current_user = await self.users_client.get_user_from_token(token)

            # Validar input data
            self._validate_post_creation(input_dto)
            await self._validate_existing_post(current_user.id)

            # Obtener o crear la ruta
            
            route = await self.routes_client.get_or_create_route(
                flightId=input_dto.flightId,
                sourceAirportCode = input_dto.origin.airportCode,
                sourceCountry = input_dto.origin.country,
                destinyAirportCode = input_dto.destiny.airportCode,
                destinyCountry = input_dto.destiny.country,
                bagCost = input_dto.bagCost,
                plannedStartDate = input_dto.plannedStartDate,
                plannedEndDate = input_dto.plannedEndDate
            )

            # crear post
            new_post_creation_request = CreatePost(
                id = route.id,
                expireAt = input_dto.expireAt,
                userId = current_user.id,
            )

            created_post = await self.posts_client.create_post(new_post_creation_request)

            return created_post
        
        except (InvalidTokenError, NoTokenError, ValidationError, ServiceCommunicationError) as e:
            raise e
        
