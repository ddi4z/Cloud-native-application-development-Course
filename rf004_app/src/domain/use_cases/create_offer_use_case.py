from src.domain.models.offer import Offer, CreatedOffer
from src.domain.use_cases.base_use_case import BaseUseCase

from src.domain.ports.create_offer_port import CreateOfferPort
from src.domain.ports.post_validation_port import PostValidationPort
from src.domain.ports.score_calculation_port import ScoreCalculationPort
from src.domain.ports.user_validation_port import UserValidationPort
from src.domain.ports.find_bagcost_route_port import FindBagCostRoutePort

from src.domain.models.user import User
from src.domain.models.score import Score
from src.domain.models.post import Post
from typing import Optional
from datetime import datetime, timezone

from src.errors import (
    UnauthorizedError,
    PostNotFoundError,
    OfferOnOwnPostError,
    InvalidOfferInputError,
    PostExpiredError,
)


class CreateOfferUseCase(BaseUseCase):
    """Use case for coreography other components to create an offer."""

    def __init__(
        self,
        user_validation: UserValidationPort,
        post_validation: PostValidationPort,
        score_calculation: ScoreCalculationPort,
        create_offer: CreateOfferPort,
        find_bagcost: FindBagCostRoutePort,
    ):
        super().__init__()
        self.user_validation = user_validation
        self.post_validation = post_validation
        self.score_calculation = score_calculation
        self.create_offer = create_offer
        self.find_bagcost = find_bagcost

    def execute(self, auth_token: str, post_id: str, offer: Offer) -> CreatedOffer:
        """Create a new offer."""
        self.logger.info(
            "[CREATE_OFFER_USE_CASE] Starting CreateOfferUseCase execution"
        )

        self.logger.info("[CREATE_OFFER_USE_CASE] pinging USERS_APP")
        self.user_validation.ping()
        self.logger.info("[CREATE_OFFER_USE_CASE] USERS_APP is up")

        self.logger.info("[CREATE_OFFER_USE_CASE] pinging OFFERS_APP")
        self.create_offer.ping()
        self.logger.info("[CREATE_OFFER_USE_CASE] OFFERS_APP is up")

        self.logger.info("[CREATE_OFFER_USE_CASE] pinging POSTS_APP")
        self.post_validation.ping()
        self.logger.info("[CREATE_OFFER_USE_CASE] POSTS_APP is up")

        if (
            offer.description is None
            or offer.size is None
            or offer.fragile is None
            or offer.offer is None
        ):
            self.logger.error("[CREATE_OFFER_USE_CASE] invalid offer properties")
            raise InvalidOfferInputError(
                "Offer values cannot be None: {description, size, fragile, offer}"
            )

        user: Optional[User] = self.user_validation.validate_token_and_get_user(
            token=auth_token
        )

        if user is None:
            self.logger.error("[CREATE_OFFER_USE_CASE] user not authorized")
            raise UnauthorizedError(f"User not authorized with token {auth_token}")

        self.logger.info(f"[CREATE_OFFER_USE_CASE] user validated: {user}")

        post: Optional[Post] = self.post_validation.validate_and_get_post(
            postId=post_id
        )

        if post is None:
            self.logger.error(
                f"[CREATE_OFFER_USE_CASE] post with id {post_id} not found"
            )
            raise PostNotFoundError(f"Post with id {post_id} not found")

        self.logger.info(f"[CREATE_OFFER_USE_CASE] post validated: {post}")

        if datetime.fromisoformat(post.expireAt) < datetime.now(timezone.utc):
            self.logger.error(
                f"[CREATE_OFFER_USE_CASE] post with id {post_id} has expired"
            )
            raise PostExpiredError(f"Post with id {post_id} has expired")

        user_id = user.id
        if post.userId == user_id:
            self.logger.error(
                f"[CREATE_OFFER_USE_CASE] user {user_id} cannot create an offer on their own post {post_id}"
            )
            raise OfferOnOwnPostError("User cannot create an offer on their own post")

        # first try to create the offer
        # if it fails, the score calculation won't be executed
        created_offer: CreatedOffer = self.create_offer.create_offer(
            offer,
            userId=user_id,
            postId=post_id,
        )

        self.logger.info(f"[CREATE_OFFER_USE_CASE] created offer: {offer}")

        bagCost = self.find_bagcost.get_bagcost(post.routeId)

        score = self.score_calculation.calculate_score(
            Score(
                offer_id=created_offer.id,
                size=offer.size,
                baggage_value=bagCost if bagCost is not None else 0,
                amount_offered=offer.offer,
            )
        )

        self.logger.info(
            f"[CREATE_OFFER_USE_CASE] score calculated for post {post_id} with size {offer.size} is {score}"
        )

        return created_offer
