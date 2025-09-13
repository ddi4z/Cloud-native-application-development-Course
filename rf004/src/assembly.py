from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_offer_use_case import CreateOfferUseCase

from src.domain.ports.user_validation_port import UserValidationPort
from src.domain.ports.post_validation_port import PostValidationPort
from src.domain.ports.score_calculation_port import ScoreCalculationPort
from src.domain.ports.create_offer_port import CreateOfferPort
from src.domain.ports.find_bagcost_route_port import FindBagCostRoutePort

from src.adapters.user_validation_adapter import UserValidationAdapter
from src.adapters.post_validation_adapter import PostValidationAdapter
from src.adapters.score_calculation_adapter import ScoreCalculationAdapter
from src.adapters.create_offer_adapter import CreateOfferAdapter
from src.adapters.fing_bagcost_route_adapter import FindBagCostRouteAdapter

import os

services = ['USERS', 'POSTS', 'SCORES', 'OFFERS', 'ROUTES']
url_services = {}

for service in services:
    service_name = f"{service}_SERVICE_URL"
    if service_name not in os.environ:
        raise EnvironmentError(f"{service}_SERVICE_URL environment variable not set")

    url_services[service] = os.environ[service_name]

user_validation_adapter: UserValidationPort = UserValidationAdapter(url_services['USERS'])
post_validation_adapter: PostValidationPort = PostValidationAdapter(url_services['POSTS'])
score_calculation_adapter: ScoreCalculationPort = ScoreCalculationAdapter(url_services['SCORES'])
create_offer_adapter: CreateOfferPort = CreateOfferAdapter(url_services['OFFERS'])
find_bagcost_route_adapter: FindBagCostRoutePort = FindBagCostRouteAdapter(url_services['ROUTES'])

def build_create_offer_use_case() -> BaseUseCase:
    """Get create offer use case."""
    return CreateOfferUseCase(
        user_validation=user_validation_adapter,
        post_validation=post_validation_adapter,
        score_calculation=score_calculation_adapter,
        create_offer=create_offer_adapter,
        find_bagcost=find_bagcost_route_adapter
    )
