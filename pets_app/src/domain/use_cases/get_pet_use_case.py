from src.domain.models.pet import Pet
from src.domain.ports.pet_repository_port import PetRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class GetPetUseCase(BaseUseCase):
    """Use case for getting a pet."""

    def __init__(self, pet_repository: PetRepositoryPort):
        self.pet_repository = pet_repository

    def execute(self, pet_id: int) -> Pet:
        return self.pet_repository.get_by_id(pet_id)
