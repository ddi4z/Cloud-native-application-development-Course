from typing import List
from src.domain.models.credit_card import CreditCard
from src.domain.ports.credit_card_repository_port import CreditCardRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase

class GetCreditCardsByUserUseCase(BaseUseCase):
    """
    Caso de uso para obtener todas las tarjetas de crédito de un usuario específico.
    """
    def __init__(self, repository: CreditCardRepositoryPort):
        """
        Inicializa el caso de uso con el repositorio de tarjetas de crédito.
        
        Args:
            repository (CreditCardRepositoryPort): El adaptador del repositorio.
        """
        self.repository = repository

    def execute(self, user_id: str) -> List[CreditCard]:
        """
        Ejecuta el caso de uso.
        
        Args:
            user_id (str): El ID del usuario cuyas tarjetas se van a buscar.
        
        Returns:
            List[CreditCard]: Una lista de las tarjetas de crédito encontradas para el usuario.
        """
        return self.repository.find_by_user_id(user_id)