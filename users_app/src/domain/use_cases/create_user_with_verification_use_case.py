from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_verify_request import UserVerifyRequest


class CreateUserWithVerificationUseCase(BaseUseCase):
    def __init__(self, create_user_uc: BaseUseCase, verify_identity_uc: BaseUseCase):
        self.create_user_uc = create_user_uc
        self.verify_identity_uc = verify_identity_uc

    def execute(self, user_dto: UserCreationRequest):
        created_user = self.create_user_uc.execute(user_dto)

        identity_verify_request = UserVerifyRequest(
            id=created_user.id,
            fullName=created_user.fullName,
            dni=created_user.dni,
            email=created_user.email,
        )
        self.verify_identity_uc.execute(identity_verify_request)

        return created_user
