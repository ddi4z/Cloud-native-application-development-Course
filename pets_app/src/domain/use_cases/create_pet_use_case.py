from src.domain.models.pet import Pet
from src.domain.ports.pet_repository_port import PetRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class CreatePetUseCase(BaseUseCase):
    """Use case for saving a pet."""

    def __init__(self, pet_repository: PetRepositoryPort):
        self.pet_repository = pet_repository

    def execute(self, pet: Pet) -> Pet:
        """Create a new pet."""
        return self.pet_repository.create(pet)
