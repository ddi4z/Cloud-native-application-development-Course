from src.domain.models.user_callback_request import UserCallbackRequest
from src.domain.use_cases.base_use_case import BaseUseCase


class UpdateUserStatusUseCase(BaseUseCase):
    def __init__(self, patch_user_uc: BaseUseCase, email_uc: BaseUseCase):
        self.patch_user_uc = patch_user_uc
        self.email_uc = email_uc

    def execute(self, user_id: str, user_dto: UserCallbackRequest):
        updated_user = self.patch_user_uc.execute(user_id, user_dto)
        self.email_uc.execute(updated_user)
        return updated_user
