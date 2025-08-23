from __future__ import annotations
from abc import ABC, abstractmethod


class BaseUseCase(ABC):
    """
    Clase base abstracta para los casos de uso.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Ejecuta el caso de uso.
        """
        raise NotImplementedError
