import pytest

from domain.models.user import User


@pytest.fixture
def valid_user_data():
    """Fixture providing valid user data."""
    return {
        "id": None,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "hashed_password_123",
        "full_name": "John Doe",
        "is_active": True,
    }


@pytest.fixture
def user_with_id():
    """Fixture providing a user with an ID."""
    return User(
        id=1,
        username="johndoe",
        email="johndoe@example.com",
        hashed_password="hashed_password_123",
        full_name="John Doe",
        is_active=True,
    )
