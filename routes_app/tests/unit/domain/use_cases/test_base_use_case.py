import pytest

from routes_app.domain.use_cases.base_use_case import BaseUseCase


def test_base_use_case_cannot_be_instantiated():
    """
    Verifica que la clase base abstracta no se puede instanciar
    y que su método execute lanza NotImplementedError.
    """

    class ConcreteUseCase(BaseUseCase):
        def execute(self):
            return super().execute()

    with pytest.raises(NotImplementedError):
        use_case = ConcreteUseCase()
        use_case.execute()
