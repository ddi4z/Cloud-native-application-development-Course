from typing import List

from src.domain.models.pet import Pet
from src.domain.ports.pet_repository_port import PetRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase


class GetAllPetsUseCase(BaseUseCase):
    """Use case for getting all pets."""

    def __init__(self, pet_repository: PetRepositoryPort):
        self.pet_repository = pet_repository

    def execute(self) -> List[Pet]:
        return self.pet_repository.get_all()
