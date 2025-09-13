from datetime import datetime, timezone
from src.domain.use_cases.base_use_case import BaseUseCase

from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort

from src.domain.models.models import (UserInput, RouteCreateInput, PublicationResponse,PublicationResponseData, CreatePost, RouteDetails)

from src.errors import ValidationError, InvalidTokenError, NoTokenError, InvalidRouteDatesError, InvalidExpiredAtError, ConflictError, ServiceCommunicationError




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


    async def execute(self, token:str, input_dto: UserInput) -> PublicationResponseData:
        """
        Executes the process of creating a post by calling the microservice responsible
        for actually creating the post.
        
        :param user_id: ID of the user creating the post
        :param content: Content of the post to be created
        :return: Response from the post creation service
        """
        
        # Validate user input is complete
        if input_dto.flightId is None or input_dto.expireAt is None or input_dto.plannedEndDate is None \
        or input_dto.plannedEndDate is None or input_dto.origin is None or input_dto.destiny is None or input_dto.bagCost is None:
            raise ValidationError('Inputs faltantes')
        
        # Validate dates are okay
            # aux variables
        current_date = datetime.now().date()
        start_date_user_input = datetime.fromisoformat(input_dto.plannedStartDate)
        expire_date_user_input = datetime.fromisoformat(input_dto.expireAt)
            
            # PlannedStartDate is in the future                        
        if start_date_user_input <= current_date:
            raise InvalidRouteDatesError('la fecha de inicio debe estar en el futuro.')

            # Expire date between current date and start date
        if not (current_date < expire_date_user_input <= start_date_user_input):
            raise InvalidExpiredAtError('La fecha de expiración debe ser posterior a fecha actual y anterior a comienzo viaje.')
        
        # Check for token
        if token is None:
            raise NoTokenError('Token no está en la solicitud')
              
        # Validate user
        current_user = await self.users_client.get_user_from_token(token=token)

        if current_user is None:
            raise InvalidTokenError('Usuario no autorizado')
        
        print(f"[LOG] user validated: {current_user}")

        # Validate if provided route already exists
        route_search = await self.routes_client.find_route_by_flightid(flightId=input_dto.flightId)

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
                plannedEndDate = input_dto.plannedStartDate
            )
            route_created = await self.routes_client.create_route(route_dto=route_to_create)
            route_id = route_created.id
        
        else:
            route_id = route_search.id

        # Check if already a post for that route_id
        post = await self.posts_client.get_post_from_userid_route_id(user_id=current_user.id, route_id=route_id)

        if post is not None:
            raise ConflictError('Usuario ya tiene ruta para ese trayecto')


        # crear post
        new_post_creation_request = CreatePost(
            id = route_id,
            expireAt = input_dto.expireAt,
            userId = current_user.id,
        )

        created_post = await self.posts_client.create_post(new_post_creation_request)


        # Final answer
        if route_search is None:
            final_answer = PublicationResponse(
                data = PublicationResponseData(
                    id = created_post.id,
                    userId=created_post.userId,
                    createdAt=created_post.createdAt,
                    expireAt=input_dto.expireAt,
                    route= RouteDetails(
                        id=route_created.id,
                        createdAt=route_created.createdAt
                    )
                ),
                msg='Resumen de la operación *.'
            )
        
        else:
            final_answer = PublicationResponse(
                data = PublicationResponseData(
                    id= created_post.id,
                    userId=created_post.userId,
                    createdAt=created_post.createdAt,
                    expireAt=input_dto.expireAt,
                    route= RouteDetails(
                        id=route_search.id,
                        createdAt=route_search.createdAt
                    )
                ),
                msg='Resumen de la operación *.'
            )

        return final_answer