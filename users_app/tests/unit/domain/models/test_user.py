import pytest
from pydantic import ValidationError
from src.domain.models.user import User


def test_create_user_with_valid_data(valid_user_data):
    """Test creating a user with valid data."""
    user = User(**valid_user_data)

    assert user.id is None
    assert user.username == valid_user_data["username"]
    assert user.email == valid_user_data["email"]
    assert user.password == valid_user_data["password"]


def test_create_user_with_id(user_with_id):
    """Test creating a user with an ID."""
    assert user_with_id.id == 1
    assert user_with_id.username == "johndoe"
    assert user_with_id.email == "johndoe@example.com"
    assert user_with_id.password == "securepassword123"


def test_create_user_with_empty_username(valid_user_data):
    """Test creating a user with an empty username."""
    with pytest.raises(ValidationError) as exc_info:
        User(**{**valid_user_data, "username": ""})

    assert "username" in str(exc_info.value)
    assert "String should have at least 1 character" in str(exc_info.value)


def test_create_user_with_invalid_email(valid_user_data):
    """Test creating a user with an invalid email format."""
    with pytest.raises(ValidationError) as exc_info:
        User(**{**valid_user_data, "email": "invalid_email"})

    assert "email" in str(exc_info.value)
    assert "value is not a valid email address" in str(exc_info.value)


def test_create_user_with_short_password(valid_user_data):
    """Test creating a user with a password that is too short."""
    with pytest.raises(ValidationError) as exc_info:
        User(**{**valid_user_data, "password": "123"})

    assert "password" in str(exc_info.value)
    assert "String should have at least" in str(exc_info.value)


def test_create_user_with_none_values():
    """Test creating a user with None values for required fields."""
    with pytest.raises(ValidationError) as exc_info:
        User(
            username=None,
            email=None,
            password=None,
        )

    assert "username" in str(exc_info.value)
    assert "email" in str(exc_info.value)
    assert "password" in str(exc_info.value)


def test_create_user_with_extra_fields(valid_user_data):
    """Test creating a user with extra fields."""
    user = User(**valid_user_data, extra_field="extra")

    assert not hasattr(user, "extra_field")


def test_user_model_equality(user_with_id):
    """Test user model equality."""
    user2 = User(id=1, username="johndoe", email="johndoe@example.com", password="securepassword123")

    assert user_with_id == user2


def test_user_model_inequality(user_with_id):
    """Test user model inequality."""
    user2 = User(id=2, username="johndoe", email="johndoe@example.com", password="securepassword123")

    assert user_with_id != user2


def test_user_model_dict_conversion(user_with_id):
    """Test user model conversion to dictionary."""
    user_dict = user_with_id.model_dump()
    assert user_dict == {
        "id": 1,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "securepassword123",
    }


def test_user_model_json_conversion(user_with_id):
    """Test user model conversion to JSON."""
    user_json = user_with_id.model_dump_json()
    assert (
        user_json
        == '{"id":1,"username":"johndoe","email":"johndoe@example.com","password":"securepassword123"}'
    )
