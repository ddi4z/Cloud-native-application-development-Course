import os

from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_verify_request import UserData, UserVerifyRequest
from src.domain.use_cases.base_use_case import BaseUseCase


class CreateUserWithVerificationUseCase(BaseUseCase):
    def __init__(self, create_user_uc: BaseUseCase, verify_identity_uc: BaseUseCase):
        self.create_user_uc = create_user_uc
        self.verify_identity_uc = verify_identity_uc
        self.webhook_base_url = os.getenv("WEBHOOK_BASE_URL", "http://localhost:9000")

    def execute(self, user_dto: UserCreationRequest):
        created_user = self.create_user_uc.execute(user_dto)

        identity_verify_request = UserVerifyRequest(
            user=UserData(
                email=created_user.email,
                dni=created_user.dni,
                fullName=created_user.fullName,
                phone=getattr(created_user, "phone", None),
            ),
            transactionIdentifier=f"txn-{created_user.id}",
            userIdentifier=str(created_user.id),
            userWebhook=f"{self.webhook_base_url}/users/status/{created_user.id}",
        )

        self.verify_identity_uc.execute(identity_verify_request)

        return created_user
