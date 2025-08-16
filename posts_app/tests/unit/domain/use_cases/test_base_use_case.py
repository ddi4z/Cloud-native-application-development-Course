import pytest
from src.domain.use_cases.base_use_case import BaseUseCase

def test_base_use_case_is_abstract_and_cannot_be_instantiated():
    with pytest.raises(TypeError, match="Can't instantiate abstract class BaseUseCase with abstract method execute"):
        BaseUseCase()

def test_subclass_without_execute_remains_abstract():
    class IncompleteUseCase(BaseUseCase):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class IncompleteUseCase with abstract method execute"):
        IncompleteUseCase()

def test_subclass_with_execute_is_concrete_and_can_be_instantiated():
    class ConcreteUseCase(BaseUseCase):
        def execute(self, data):
            return f"Executing with {data}"

    try:
        use_case = ConcreteUseCase()
        assert isinstance(use_case, ConcreteUseCase)
    except TypeError:
        pytest.fail("Se esperaba que ConcreteUseCase fuera instanciable después de implementar 'execute'.")

def test_concrete_subclass_execute_method_works_as_expected():
    class ConcreteUseCase(BaseUseCase):
        def execute(self, data):
            return f"Executing with {data}"

    use_case = ConcreteUseCase()
    result = use_case.execute("test_data")
    assert result == "Executing with test_data"