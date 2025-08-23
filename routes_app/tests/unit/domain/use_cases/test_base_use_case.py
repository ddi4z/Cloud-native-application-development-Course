import pytest
from src.routes_app.domain.use_cases.base_use_case import BaseUseCase

def test_base_use_case_is_abstract():
    with pytest.raises(TypeError):
        BaseUseCase()  